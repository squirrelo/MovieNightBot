import logging

import discord
from discord import app_commands

from movienightbot.util import is_channel


logger = logging.getLogger("movienightbot")


@app_commands.command(description="Posts a link to all movies that have been watched.")
@app_commands.check(is_channel)
async def watched(interaction: discord.Interaction):
    from ..application import bot

    await interaction.response.send_message(
        f"Watched movies can be found at {bot.config.base_url}/movies.html?server={interaction.guild.id}&view=watched"
    )


@watched.error
async def watched_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        "Wrong channel used for messages. Please use the correct channel",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(watched)
    logger.info("Loaded watched command")
