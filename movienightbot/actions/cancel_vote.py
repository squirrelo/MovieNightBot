import discord
import peewee as pw

from . import BaseAction
from ..db.controllers import VoteController


class CancelVoteAction(BaseAction):
    action_name = "cancel_vote"
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

        embed = discord.Embed(
            title=f"Vote Cancelled",
            description=f"Vote was cancelled. Get better movies.",
        )
        self.controller.cancel_vote(server_id)
        vote_msg = await msg.channel.fetch_message(vote_msg_id)
        await vote_msg.unpin()
        await vote_msg.clear_reactions()
        await vote_msg.edit(content=None, embed=embed)

    @property
    def help_text(self):
        return "Cancels the currently running vote."
