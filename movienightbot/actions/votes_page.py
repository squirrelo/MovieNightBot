from . import BaseAction
from ..db.controllers import MoviesController


class VotesPageAction(BaseAction):
    action_name = "votes_page"
    controller = MoviesController()

    async def action(self, msg):
        from ..application import client

        await msg.channel.send(
            f"The active vote can be found at {client.config.base_url}/vote.html?server={msg.guild.id}"
        )

    @property
    def help_text(self):
        return "Posts a link to the server's vote page."
