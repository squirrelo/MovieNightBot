import logging

import discord
from discord import app_commands

from movienightbot.util import (
    is_channel,
    capitalize_movie_name,
)
from movienightbot.db.controllers import MoviesController, ServerController

movies_controller = MoviesController()
server_controller = ServerController()

logger = logging.getLogger("movienightbot")


@app_commands.command(description="Overrides the automatically found IMDB id for a movie with the given IMDB id")
@app_commands.check(is_channel)
async def set_imdb_id(interaction: discord.Interaction, imdb_id: str, movie: str):
    server_id = interaction.guild.id
    server_row = server_controller.get_by_id(server_id)
    message_timeout = None if server_row.message_timeout == 0 else server_row.message_timeout
    movie_name = capitalize_movie_name(movie)
    updated_rows = movies_controller.update_imdb_id(server_id, movie_name, imdb_id)

    if updated_rows == 1:
        message = f"Movie {movie_name} has been updated to imdb ID {imdb_id}"
    elif updated_rows == 0:
        message = f"Unable to update IMDB id for {movie_name}"
    else:
        message = f"Movie {movie_name} updated multiple entries to IMDB id {imdb_id}"

    await interaction.response.send_message(message, delete_after=message_timeout)


@set_imdb_id.error
async def set_imdb_id_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        f"Wrong channel used for messages. Please use the correct channel.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(set_imdb_id)
    logger.info("Loaded set_imdb_id command")
