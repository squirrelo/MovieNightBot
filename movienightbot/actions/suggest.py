import peewee as pw

from . import BaseAction
from ..db.controllers import MoviesController


class SuggestAction(BaseAction):
    action_name = "suggest"
    controller = MoviesController()

    async def action(self, msg):
        suggestion = self.get_message_data(msg)
        suggestion = suggestion.title()
        movie_data = {
            "server": msg.guild.id,
            "movie_name": suggestion,
            "suggested_by": msg.author.name,
        }
        try:
            self.controller.create(movie_data)
        except pw.IntegrityError:
            await msg.channel.send(
                f"{suggestion} has already been suggested in this server."
            )
            return
        await msg.channel.send(
            f"Your suggestion of {suggestion} has been added to the list."
        )

    @property
    def help_text(self):
        return (
            "Adds the supplied movie to the suggestions list. There is a chance this movie will now "
            "show up on future votes"
        )
