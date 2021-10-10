import peewee as pw
import logging

from . import BaseAction
from ..exc import VoteError
from ..db.controllers import VoteController
from ..util import build_vote_embed, add_vote_emojis

logger = logging.getLogger("movienightbot")


class StartVoteAction(BaseAction):
    action_name = "start_vote"
    admin = True
    controller = VoteController()

    async def action(self, msg):
        server_id = msg.guild.id
        genre = self.get_message_data(msg, 1)
        if not genre:
            genre = None

        with self.controller.transaction():
            try:
                vote_row = self.controller.start_vote(server_id, genre=genre)
            except pw.IntegrityError:
                await msg.channel.send("Vote already started!")
                return
            except VoteError:
                err_msg = "No movies found"
                if genre:
                    err_msg += f" for genre {genre}"
                await msg.channel.send(err_msg)
                return
            embed = build_vote_embed(server_id)
            vote_msg = await msg.channel.send(content=None, embed=embed)
            vote_row.message_id = vote_msg.id
            vote_row.channel_id = vote_msg.channel.id
            self.controller.update(vote_row)
            await add_vote_emojis(vote_msg, vote_row.movie_votes)
            await vote_msg.pin()

    @property
    def help_text(self):
        return "Selects a number of random movie suggestions to be voted on."
