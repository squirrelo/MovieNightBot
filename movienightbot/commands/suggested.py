from . import BaseAction
from ..db.controllers import MoviesController


class SuggestedAction(BaseAction):
    action_name = "suggested"
    controller = MoviesController()

    async def action(self, msg):
        from ..application import client

        await msg.channel.send(
            f"Suggestions can be found at {client.config.base_url}/movies.html?server={msg.guild.id}&view=suggested"
        )

    @property
    def help_text(self):
        return "Lists all movies that have been suggested."
