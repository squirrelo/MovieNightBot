import datetime

import peewee as pw

from . import BaseAction
from ..db.controllers import MoviesController


class SetWatchedAction(BaseAction):
    action_name = "set_watched"
    admin = True
    controller = MoviesController()

    async def action(self, msg):
        watched = self.get_message_data(msg)
        watched = watched.title()
        with self.controller.transaction():
            try:
                movie = self.controller.get_by_server_and_id(
                    server_id=msg.guild.id, movie=watched
                )
            except pw.DoesNotExist:
                await msg.channel.send(f"No movie titled {watched} has been suggested")
                return
            movie.watched_on = datetime.datetime.utcnow()
            self.controller.update(movie)
        await msg.channel.send(
            f"{watched} has been set as watched and will no longer show up in future votes."
        )

    @property
    def help_text(self):
        return (
            "Sets the specified movie as having been watched. This movie will not show up on "
            "future votes."
        )

    @property
    def help_options(self):
        return ["[movie_name]"]
