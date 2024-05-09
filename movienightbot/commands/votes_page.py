import logging

import discord
from discord import app_commands

logger = logging.getLogger("movienightbot")


@app_commands.command(description="Posts a link to the server's vote page.")
async def votes_page(interaction: discord.Interaction):
    from ..application import bot

    await interaction.response.send_message(
        f"The active vote can be found at {bot.config.base_url}/vote.html?server={interaction.guild.id}",
    )


@votes_page.error
async def votes_page_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        "Something went wrong during the execution of this command. I guess you should just go do something else.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(votes_page)
    logger.info("Loaded votes_page command")
