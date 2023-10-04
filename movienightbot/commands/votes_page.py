import logging

import discord
from discord import app_commands

from ..util import is_channel

logger = logging.getLogger("movienightbot")


@app_commands.command(description="Posts a link to the server's vote page.")
@app_commands.check(is_channel)
async def votes_page(interaction: discord.Interaction):
    from ..application import bot

    await interaction.response.send_message(
        f"The active vote can be found at {bot.config.base_url}/vote.html?server={interaction.guild.id}"
    )


@votes_page.error
async def votes_page_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        f"Wrong channel used for messages. Please use the correct channel",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(votes_page)
    logger.info("Loaded votes_page command")
