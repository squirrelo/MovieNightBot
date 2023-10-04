import logging

import discord
from discord import app_commands
from peewee import DoesNotExist

from ..util import get_message, is_channel, is_admin
from ..db.controllers import VoteController

vote_controller = VoteController()

logger = logging.getLogger("movienightbot")


@app_commands.command(description="[ADMIN COMMAND] Cancels the currently running vote.")
@app_commands.check(is_channel)
@app_commands.check(is_admin)
async def cancel_vote(interaction: discord.Interaction):
    server_id = interaction.guild.id
    with vote_controller.transaction():
        try:
            vote_msg_id = vote_controller.get_by_id(server_id).message_id
        except DoesNotExist:
            await interaction.response.send_message("No vote started!", ephemeral=True)
            return

    vote_controller.cancel_vote(server_id)
    vote_msg = await get_message(interaction.channel, vote_msg_id)
    if vote_msg:
        embed = discord.Embed(
            title="Vote Cancelled",
            description="Vote was cancelled. Get better movies.",
        )
        await vote_msg.clear_reactions()
        await vote_msg.edit(content=None, embed=embed)
        await vote_msg.unpin()
    await interaction.response.send_message("Vote cancelled")


@cancel_vote.error
async def cancel_vote_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        "Wrong channel used for messages or not an admin. Please use the correct channel.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(cancel_vote)
    logger.info("Loaded cancel_vote command")
