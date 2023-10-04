import logging

import discord
from discord import app_commands
import peewee as pw

from ..db.controllers import MoviesController, ServerController
from ..util import capitalize_movie_name, is_channel, is_admin

server_controller = ServerController()
movies_controller = MoviesController()

logger = logging.getLogger("movienightbot")


@app_commands.command(description="Link to all movies that have been suggested.")
@app_commands.check(is_channel)
@app_commands.check(is_admin)
async def unwatch(interaction: discord.Interaction, movie: str):
    unwatch = capitalize_movie_name(movie)
    with movies_controller.transaction():
        try:
            movie = movies_controller.get_by_server_and_id(server_id=interaction.guild.id, movie=movie)
        except pw.DoesNotExist:
            await interaction.response.send_message(f"No movie titled {unwatch} has been watched", ephemeral=True)
            return
        movie.watched_on = None
        movies_controller.update(movie)

    server_id = interaction.guild.id
    server_row = server_controller.get_by_id(server_id)
    message_timeout = None if server_row.message_timeout == 0 else server_row.message_timeout
    await interaction.response.send_message(
        f"{unwatch} has been set as unwatched and will show up in future votes.",
        delete_after=message_timeout,
    )


@unwatch.error
async def suggest_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        f"Wrong channel used for messages or not an admin. Please use the correct channel.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(unwatch)
    logger.info("Loaded unwatch command")
