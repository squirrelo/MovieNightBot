from . import BaseAction
from ..db.controllers import MoviesController


class SuggestedAction(BaseAction):
    action_name = "suggested"
    controller = MoviesController()

    async def action(self, msg):
        from ..application import client

        return (
            msg.channel,
            f"Suggestions can be found at {client.config.base_url}/suggested/{msg.guild.id}",
        )

    @property
    def help_text(self):
        return "Lists all movies that have been suggested."
