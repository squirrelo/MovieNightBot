import logging
from typing import Optional

import discord
from discord import app_commands
from peewee import IntegrityError

from movienightbot.exc import VoteError
from movienightbot.util import is_admin, is_channel, build_vote_embed, add_vote_emojis
from movienightbot.db.controllers import VoteController

logger = logging.getLogger("movienightbot")

vote_controller = VoteController()


@app_commands.command(description="[ADMIN COMMAND] Starts the vote. Filters to the given list of genres. Separate "
                                  "genres by spaces within the argument.")
@app_commands.check(is_channel)
@app_commands.check(is_admin)
async def start_vote(interaction: discord.Interaction, genres: Optional[str] = None):
    if genres:
        genres = genres.lower().split(' ')  # split by space since user can have spaces in command arguments
    # await interaction.response.send_message(f"{len(genre)} generes included {', '.join(genre)}", ephemeral=True)

    server_id = interaction.guild.id
    with vote_controller.transaction():
        try:
            vote_row = vote_controller.start_vote(server_id, genres=genres)
        except IntegrityError:
            await interaction.response.send_message("Vote already started!", ephemeral=True)
            return
        except VoteError:
            err_msg = "No movies found"
            if genres:
                err_msg += f" for genre(s) {', '.join(genres)}"
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
        "Wrong channel used for messages or not an admin. Please use the correct channel.",
        ephemeral=True,
    )
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(start_vote)
    logger.info("Loaded start_vote command")
