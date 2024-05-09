import logging

import discord
from discord import app_commands


logger = logging.getLogger("movienightbot")


@app_commands.command(description="Posts a link to all movies that have been suggested.")
async def suggested(interaction: discord.Interaction):
    from ..application import bot

    await interaction.response.send_message(
        f"Suggestions can be found at {bot.config.base_url}/movies.html?server={interaction.guild.id}&view=suggested",
    )


@suggested.error
async def suggest_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        "Something went wrong during the execution of this command. I guess you should just go do something else..",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(suggested)
    logger.info("Loaded suggested command")
