from typing import Union, Tuple, List

import peewee as pw
import imdb

from . import BaseAction
from ..db.controllers import (
    MoviesController,
    GenreController,
    ServerController,
    IMDBInfoController,
    IMDBInfo,
)
from ..util import get_imdb_info, cleanup_messages, capitalize_movie_name
from . import logger


class SuggestAction(BaseAction):
    action_name = "suggest"
    controller = MoviesController()
    server_controller = ServerController()
    imdb_controller = IMDBInfoController()
    genre_controller = GenreController()

    def imdb_data(self, msg, kind) -> Tuple[Union[None, IMDBInfo], Union[None, imdb.Movie.Movie]]:
        suggestion = capitalize_movie_name(self.get_message_data(msg))
        imdb_info = get_imdb_info(suggestion, kind=kind)
        if not imdb_info:
            return None, None
        # see if the row already exists
        try:
            imdb_row = self.imdb_controller.get_by_id(imdb_info.movieID)
        except pw.DoesNotExist:
            pass
        else:
            return imdb_row, imdb_info
        # row doesnt exist, so add it
        imdb_data = {
            "imdb_id": imdb_info.movieID,
            "title": imdb_info["title"],
            "canonical_title": imdb_info["canonical title"],
            "year": imdb_info["year"],
            "thumbnail_poster_url": imdb_info["cover url"],
            "full_size_poster_url": imdb_info["full-size cover url"],
        }
        try:
            imdb_row = self.imdb_controller.create(imdb_data)
        except pw.IntegrityError as e:
            logger.error("IMDB entry insert error: {}\n{}".format(imdb_data, str(e)))
            return None, None
        return imdb_row, imdb_info

    def add_genre_info(self, server_id: int, movie_name: str, genres: List[str]) -> None:
        clean_movie_name = capitalize_movie_name(movie_name)
        for genre in genres:
            self.genre_controller.add_genre_to_movie(server_id, clean_movie_name, genre)

    async def action(self, msg):
        server_id = msg.guild.id
        server_row = self.server_controller.get_by_id(server_id)
        message_timeout = server_row.message_timeout
        if server_row.block_suggestions:
            server_msg = await msg.channel.send("Suggestions are currently disabled on the server")
            await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
            return

        if server_row.check_movie_names:
            allow_tv_shows = server_row.allow_tv_shows
            kind = None if allow_tv_shows else "movie"
            imdb_row, imdb_info = self.imdb_data(msg, kind=kind)
            suggestion = (
                capitalize_movie_name(imdb_row.title) if imdb_row else capitalize_movie_name(self.get_message_data(msg))
            )
            if imdb_row is None:
                server_msg = await msg.channel.send("Could not find the movie title you suggested in IMDb.")
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
                return
        else:
            imdb_row, imdb_info = None, None
            suggestion = capitalize_movie_name(self.get_message_data(msg))

        movie_data = {
            "server": server_id,
            "movie_name": suggestion,
            "suggested_by": msg.author.name,
            "imdb_id": imdb_row,
        }
        movie_row = None
        try:
            if imdb_row is None:
                try:
                    movie_row = self.controller.get_by_server_and_id(server_id, suggestion)
                except pw.DoesNotExist:
                    # Movie not found, and no IMDB info to go by, so keep going
                    pass
                else:
                    raise pw.IntegrityError("Already suggested, but no IMDB info given")
            self.controller.create(movie_data)
        except pw.IntegrityError as e:
            logger.debug("Movie insert error: {}\n{}".format(movie_data, str(e)))
            movie_status = "watched" if movie_row and movie_row.watched_on else "suggested"
            server_msg = await msg.channel.send(f"{suggestion} has already been {movie_status} in this server.")
            await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
            return

        if imdb_info:
            try:
                self.add_genre_info(server_id, suggestion, imdb_info["genres"])
            except pw.IntegrityError as e:
                logger.error(f"Genre insert error: {server_id} {imdb_info['genres']} {suggestion}\n{e}")
                server_msg = await msg.channel.send(f"Error adding suggestion {suggestion}")
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
                return

        server_msg = await msg.channel.send(
            f"Your suggestion of {suggestion} ({imdb_row.year if imdb_row else ''}) has been added to the list."
        )
        await cleanup_messages([msg, server_msg], sec_delay=message_timeout)

    @property
    def help_text(self):
        return (
            "Adds the supplied movie to the suggestions list. There is a chance this movie will now "
            "show up on future votes"
        )

    @property
    def help_options(self):
        return ["[movie name]"]
