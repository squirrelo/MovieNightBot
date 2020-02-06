from . import BaseAction


class EndVoteAction(BaseAction):
    action_name = "end_vote"

    def break_tie(self):
        raise NotImplementedError()

    async def action(self, msg):
        await msg.channel.send(f"`{self.action_name}` command still being implemented!")

    @property
    def help_text(self):
        return (
            "Ends the currently running vote and displays the winning vote. Reacting to the vote "
            "embed with :octagonal_sign: will also end the vote."
        )
