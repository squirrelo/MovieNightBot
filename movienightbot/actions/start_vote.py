from typing import List

from . import BaseAction
from ..db.models import Server, MovieVote
from ..util import build_vote_embed


class StartVoteAction(BaseAction):
    action_name = "start_vote"
    admin = True

    async def action(self, msg):
        await msg.channel.send(f"`{self.action_name}` command still being implemented!")

    @property
    def help_text(self):
        return "Selects a number of random movie suggestions to be voted on."
