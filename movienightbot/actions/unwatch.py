import peewee as pw

from . import BaseAction
from ..db.controllers import MoviesController


class UnwatchAction(BaseAction):
    action_name = "unwatch"
    admin = True
    controller = MoviesController()

    async def action(self, msg):
        unwatch = self.get_message_data(msg)
        unwatch = unwatch.title()
        with self.controller.transaction():
            try:
                movie = self.controller.get_by_server_and_id(
                    server_id=msg.guild.id, movie=unwatch
                )
            except pw.DoesNotExist:
                await msg.channel.send(f"No movie titled {unwatch} has been watched")
                return
            movie.watched_on = None
            self.controller.update(movie)
        await msg.channel.send(
            f"{unwatch} has been set as unwatched and will show up in future votes."
        )

    @property
    def help_text(self):
        return "Removes the specified movie from the watched list."
