import logging

import discord
from discord import app_commands
from peewee import IntegrityError

from movienightbot.util import (
    capitalize_movie_name,
    is_channel,
)
from movienightbot.db.controllers import GenreController, ServerController

genre_controller = GenreController()
server_controller = ServerController()

logger = logging.getLogger("movienightbot")


@app_commands.command(description="Adds a genre to a movie manually.")
@app_commands.check(is_channel)
async def set_genre(interaction: discord.Interaction, genre: str, movie_name: str):
    server_id = interaction.guild.id
    server_row = server_controller.get_by_id(server_id)
    message_timeout = None if server_row.message_timeout == 0 else server_row.message_timeout
    genre = genre.lower()
    movie_name = capitalize_movie_name(movie_name)
    try:
        genre_controller.add_genre_to_movie(server_id, movie_name, genre)
    except IntegrityError as e:
        logger.debug(f"Genre add error: {server_id} {movie_name} {genre}\n{e}")
        await interaction.channel.send_message(f"{movie_name} already has genre {genre}", ephemeral=True)
        return
    message_timeout = None if message_timeout == 0 else message_timeout
    await interaction.response.send_message(
        f"Movie {movie_name} has been updated with genre {genre}",
        delete_after=message_timeout,
    )


@set_genre.error
async def set_genre_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        "Wrong channel used for messages. Please use the correct channel.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(set_genre)
    logger.info("Loaded set_genre command")
