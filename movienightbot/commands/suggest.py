import logging
from typing import List, Tuple, Union

import discord
import imdb
from discord import app_commands
from peewee import DoesNotExist, IntegrityError

from movienightbot.util import is_channel, capitalize_movie_name, get_imdb_info
from movienightbot.db.controllers import (
    MoviesController,
    ServerController,
    IMDBInfo,
    IMDBInfoController,
    GenreController,
)

logger = logging.getLogger("movienightbot")

movies_controller = MoviesController()
server_controller = ServerController()
imdb_controller = IMDBInfoController()
genre_controller = GenreController()


def imdb_data(movie: str, kind: str) -> Tuple[Union[None, IMDBInfo], Union[None, imdb.Movie.Movie]]:
    suggestion = capitalize_movie_name(movie)
    imdb_info = get_imdb_info(suggestion, kind=kind)
    if not imdb_info:
        return None, None
    # see if the row already exists
    try:
        imdb_row = imdb_controller.get_by_id(imdb_info.movieID)
    except DoesNotExist:
        pass
    else:
        return imdb_row, imdb_info

    # row doesn't exist, so add it
    imdb_row_data = {
        "imdb_id": imdb_info.movieID,
        "title": imdb_info["title"],
        "canonical_title": imdb_info["canonical title"],
        "year": imdb_info["year"],
        "thumbnail_poster_url": imdb_info["cover url"],
        "full_size_poster_url": imdb_info["full-size cover url"],
    }
    try:
        imdb_row = imdb_controller.create(imdb_row_data)
    except IntegrityError as e:
        logger.error("IMDB entry insert error: {}\n{}".format(imdb_data, str(e)))
        return None, None
    return imdb_row, imdb_info


def add_genre_info(server_id: int, movie_name: str, genres: List[str]) -> None:
    clean_movie_name = capitalize_movie_name(movie_name)
    for genre in genres:
        genre_controller.add_genre_to_movie(server_id, clean_movie_name, genre)


@app_commands.command(description="Adds the movie to the suggestions list for future votes.")
@app_commands.check(is_channel)
async def suggest(interaction: discord.Interaction, movie: str):
    await interaction.response.defer()
    server_id = interaction.guild.id
    server_row = server_controller.get_by_id(server_id)
    if server_row.block_suggestions:
        await interaction.followup.send("Suggestions are currently disabled on the server", ephemeral=True)
        return

    if server_row.check_movie_names:
        allow_tv_shows = server_row.allow_tv_shows
        kind = None if allow_tv_shows else "movie"
        imdb_row, imdb_info = imdb_data(movie=movie, kind=kind)
        suggestion = capitalize_movie_name(imdb_row.title) if imdb_row else capitalize_movie_name(movie)
        if imdb_row is None:
            await interaction.followup.send("Could not find the movie title you suggested in IMDb.", ephemeral=True)
            return
    else:
        imdb_row, imdb_info = None, None
        suggestion = capitalize_movie_name(movie)

    movie_data = {
        "server": server_id,
        "movie_name": suggestion,
        "suggested_by": interaction.user.name,
        "imdb_id": imdb_row,
    }
    movie_row = None
    try:
        if imdb_row is None:
            try:
                movie_row = movies_controller.get_by_server_and_id(server_id, suggestion)
            except DoesNotExist:
                # Movie not found, and no IMDB info to go by, so keep going
                pass
            else:
                raise IntegrityError("Already suggested, but no IMDB info given")
        movies_controller.create(movie_data)
    except IntegrityError as e:
        logger.debug("Movie insert error: {}\n{}".format(movie_data, str(e)))
        movie_status = "watched" if movie_row and movie_row.watched_on else "suggested"
        await interaction.followup.send(f"{suggestion} has already been {movie_status} in this server.")
        return

    if imdb_info:
        try:
            add_genre_info(server_id, suggestion, imdb_info["genres"])
        except IntegrityError as e:
            logger.error(f"Genre insert error: {server_id} {imdb_info['genres']} {suggestion}\n{e}")
            await interaction.followup.send(f"Error adding suggestion {suggestion}")
            return

    await interaction.followup.send(
        f"Your suggestion of {suggestion} ({imdb_row.year if imdb_row else ''}) has been added to the list.",
    )


@suggest.error
async def suggest_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.followup.send(
        "Wrong channel used for messages. Please use the correct channel.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(suggest)
    logger.info("Loaded suggest command")
