import logging
from typing import Optional

import discord
from discord import app_commands
from peewee import IntegrityError

from movienightbot.db.controllers import VoteController
from movienightbot.exc import VoteError
from movienightbot.util import add_vote_emojis, build_vote_embed, is_admin

logger = logging.getLogger("movienightbot")

vote_controller = VoteController()


@app_commands.command(description="[ADMIN COMMAND] Starts the vote. Filters to only genre, if given.")
@app_commands.check(is_admin)
async def start_vote(interaction: discord.Interaction, genre: Optional[str] = None):
    server_id = interaction.guild.id
    with vote_controller.transaction():
        try:
            vote_row = vote_controller.start_vote(server_id, genre=genre)
        except IntegrityError:
            await interaction.response.send_message("Vote already started!", ephemeral=True)
            return
        except VoteError:
            err_msg = "No movies found"
            if genre:
                err_msg += f" for genre {genre}"
            await interaction.response.send_message(err_msg)
            return
        embed = build_vote_embed(server_id)
        vote_msg = await interaction.channel.send(content=None, embed=embed)
        vote_row.message_id = vote_msg.id
        vote_row.channel_id = vote_msg.channel.id
        vote_controller.update(vote_row)
        await add_vote_emojis(vote_msg, vote_row.movie_votes)
        await vote_msg.pin()


@start_vote.error
async def start_vote_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(
        "Something went wrong during the execution of this command. I guess you should just go do something else.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(start_vote)
    logger.info("Loaded start_vote command")
