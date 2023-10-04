import logging
import re

import discord
from discord import app_commands
from peewee import DoesNotExist

from movienightbot.util import get_message, build_vote_embed, add_vote_emojis, is_channel
from movienightbot.db.controllers import VoteController, ServerController

vote_controller = VoteController()
server_controller = ServerController()

logger = logging.getLogger("movienightbot")


async def end_vote_task(interaction: discord.Interaction):
    server_id = interaction.guild.id
    with vote_controller.transaction():
        try:
            vote_msg_id = vote_controller.get_by_id(server_id).message_id
        except DoesNotExist:
            await interaction.response.send_message("No vote started!")
            return
        winning_movies = vote_controller.end_vote(server_id)
    # TODO: Make more robust so we don't assume the end message and vote message are in same channel
    # probably safe for now, only happens if admin changes bot channel in the middle of a vote
    vote_msg = await get_message(interaction.channel, vote_msg_id)
    if vote_msg:
        await vote_msg.clear_reactions()
    else:
        # Vote message was deleted or is unavailable, so make a new one
        vote_msg = await interaction.channel.send("replacement vote message")
    if len(winning_movies) == 1:
        winning_movie = winning_movies[0].movie_name
        imdb_info = winning_movies[0].imdb_id
        if imdb_info:
            imdb_url = f"https://www.imdb.com/title/tt{imdb_info.imdb_id}/"
            imdb_markup_link = f"[IMDb Page]({imdb_url})"
            imdb_year = f"({imdb_info.year})"
        else:
            imdb_url, imdb_markup_link, imdb_year = "", "", ""

        embed = discord.Embed(
            title=f"Wining movie: {winning_movie} {imdb_year}",
            description=f"{imdb_markup_link} Use `m!set_watched {winning_movie}` to set the movie as watched",
        )
        await interaction.response.send_message(
            f"The winning vote was `{winning_movie}`! "
            f"To set the movie as watched use the command `m!set_watched {winning_movie}`"
        )
        await vote_msg.unpin()
    else:
        await interaction.response.send_message("There was a tie! Check the vote message for new vote options")
        with vote_controller.transaction():
            server_row = server_controller.get_by_id(server_id)
            if server_row.tie_option == "breaker":
                vote_row = vote_controller.start_runoff_vote(server_id, vote_msg, winning_movies)
            elif server_row.tie_option == "random":
                vote_row = vote_controller.start_vote(server_id)
                vote_row.message_id = vote_msg.id
                vote_row.channel_id = vote_msg.channel.id
                vote_controller.update(vote_row)
        embed = build_vote_embed(server_id)
        await add_vote_emojis(vote_msg, vote_row.movie_votes)
    await vote_msg.edit(content=None, embed=embed)


@app_commands.command(description="Ends the currently running vote and displays the winning vote.")
@app_commands.check(is_channel)
async def end_vote(interaction: discord.Interaction):
    await end_vote_task(interaction)


@end_vote.error
async def end_vote_error(interaction: discord.Interaction, error: discord.app_commands.errors.CheckFailure):
    await interaction.response.send_message(f"Wrong channel used for messages. Please use the correct channel", ephemeral=True)
    logger.debug(str(error))


async def setup(bot):
    bot.tree.add_command(end_vote)
    logger.info("Loaded end_vote command")
