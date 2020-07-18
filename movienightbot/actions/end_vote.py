import discord
import peewee as pw

from . import BaseAction
from ..db.controllers import VoteController, ServerController
from ..util import build_vote_embed, add_vote_emojis


class EndVoteAction(BaseAction):
    action_name = "end_vote"
    controller = VoteController()

    def break_tie(self):
        raise NotImplementedError()

    async def action(self, msg):
        server_id = msg.guild.id
        with self.controller.transaction():
            try:
                vote_msg_id = self.controller.get_by_id(server_id).message_id
            except pw.DoesNotExist:
                await msg.channel.send("No vote started!")
                return
            winning_movies = self.controller.end_vote(server_id)
        # TODO: Make more robust so we don't assume the end message and vote message are in same channel
        # probably safe for now, only happens if admin changes bot channel in the middle of a vote
        vote_msg = await msg.channel.fetch_message(vote_msg_id)
        await vote_msg.clear_reactions()
        if len(winning_movies) == 1:
            winning_movie = winning_movies[0].movie_name
            embed = discord.Embed(
                title=f"Wining movie: {winning_movie}",
                description=f"Use `m!set_watched {winning_movie}` to set the movie as watched",
            )
            await msg.channel.send(
                f"The winning vote was `{winning_movie}`! "
                f"To set the movie as watched use the command `m!set_watched {winning_movie}`"
            )
            await vote_msg.unpin()
        else:
            await msg.channel.send(
                "There was a tie! Check the vote message for new vote options"
            )
            with self.controller.transaction():
                server_row = ServerController().get_by_id(server_id)
                if server_row.tie_option == "breaker":
                    vote_row = self.controller.start_runoff_vote(
                        server_id, vote_msg, winning_movies
                    )
                elif server_row.tie_option == "random":
                    vote_row = self.controller.start_vote(server_id)
                    vote_row.message_id = vote_msg.id
                    vote_row.channel_id = vote_msg.channel.id
                    self.controller.update(vote_row)
            embed = build_vote_embed(server_id)
            await add_vote_emojis(vote_msg, vote_row.movie_votes)
        await vote_msg.edit(content=None, embed=embed)

    @property
    def help_text(self):
        return (
            "Ends the currently running vote and displays the winning vote. Reacting to the vote "
            "embed with :octagonal_sign: will also end the vote."
        )
