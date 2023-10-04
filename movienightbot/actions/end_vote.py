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

    

    @property
    def help_text(self):
        return (
            Reacting to the vote "
            "embed with :octagonal_sign: will also end the vote."
        )
