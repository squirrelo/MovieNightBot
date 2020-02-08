import discord
import peewee as pw

from . import BaseAction
from ..db.controllers import VoteController


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
            except pw.IntegrityError:
                await msg.channel.send("No vote started!")
                return
            winning_movies = self.controller.end_vote(server_id)
        # TODO: Make more robust so we don't assume the end message and vote message are in same channel
        # probably safe for now, only happens if admin changes bot channel in the middle of a vote
        vote_msg = await msg.channel.fetch_message(vote_msg_id)
        if len(winning_movies) == 1:
            embed = discord.Embed(
                title=f"Wining movie: {winning_movies[0].movie_name}",
                description=f"Use `m!set_watched {winning_movies[0].movie_name}` to set the movie as watched",
            )
        else:
            embed = discord.Embed(
                title=f"Wining movies: {', '.join(w.movie_name for w in winning_movies)}",
                description=f"Use `m!set_watched [movie name]` to set a movie as watched",
            )
        await vote_msg.edit(content=None, embed=embed)
        await vote_msg.clear_reactions()

    @property
    def help_text(self):
        return (
            "Ends the currently running vote and displays the winning vote. Reacting to the vote "
            "embed with :octagonal_sign: will also end the vote."
        )
