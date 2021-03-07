from . import BaseAction
from ..db.controllers import ServerController


class TieAction(BaseAction):
    action_name = "tie_option"
    admin = True
    controller = ServerController()

    tie_options = {"breaker", "random"}

    async def action(self, msg):
        tie_option = self.get_message_data(msg)
        if tie_option not in self.tie_options:
            return (msg.channel, f"Unknown tiebreaker option given: {tie_option}")
        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.tie_option = tie_option
            self.controller.update(server_row)
        return (msg.channel, f"Tiebreaker updated to {tie_option}")

    @property
    def help_text(self):
        return """Sets how the bot handles tied votes.
Option `breaker` will make a new vote using only the tied movies (this is the default).
Option `random` will make a new vote with a random selection of movies."""

    @property
    def help_options(self):
        return ["({})".format("|".join(self.tie_options))]
