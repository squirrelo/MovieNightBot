import logging
import datetime

import discord
from discord import app_commands
from peewee import DoesNotExist

from movienightbot.util import (
    is_channel,
    capitalize_movie_name,
)
from movienightbot.db.controllers import ServerController, MoviesController

movies_controller = MoviesController()
server_controller = ServerController()

logger = logging.getLogger("movienightbot")


@app_commands.command(description="Sets the specified movie to watched. This movie will not show up on future votes.")
@app_commands.check(is_channel)
async def set_watched(interaction: discord.Interaction, movie: str):
    watched = capitalize_movie_name(movie)

    with movies_controller.transaction():
        try:
            movie = movies_controller.get_by_server_and_id(server_id=interaction.guild.id, movie=watched)
        except DoesNotExist:
            await interaction.response.send_message(f"No movie titled {watched} has been suggested", ephemeral=True)
            return
        movie.watched_on = datetime.datetime.utcnow()
        movies_controller.update(movie)

    server_id = interaction.guild.id
    server_row = server_controller.get_by_id(server_id)
    message_timeout = None if server_row.message_timeout == 0 else server_row.message_timeout
    await interaction.response.send_message(
        f"{watched} has been set as watched and will no longer show up in future votes.",
        delete_after=message_timeout,
    )
