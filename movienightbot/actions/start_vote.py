import discord
import peewee as pw
import logging

from . import BaseAction
from ..db.controllers import VoteController
from ..util import build_vote_embed, add_vote_emojis

logger = logging.getLogger("movienightbot")


class StartVoteAction(BaseAction):
    action_name = "start_vote"
    admin = True
    controller = VoteController()

    async def action(self, msg):
        server_id = msg.guild.id
        with self.controller.transaction():
            try:
                vote_row = self.controller.start_vote(server_id)
            except pw.IntegrityError:
                await msg.channel.send("Vote already started!")
                return
            embed = build_vote_embed(server_id)
            vote_msg = await msg.channel.send(content=None, embed=embed)
            vote_row.message_id = vote_msg.id
            vote_row.channel_id = vote_msg.channel.id
            self.controller.update(vote_row)
            await add_vote_emojis(vote_msg, vote_row.movie_votes)

    @property
    def help_text(self):
        return "Selects a number of random movie suggestions to be voted on."
