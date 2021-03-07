import peewee as pw

from . import BaseAction
from ..db.controllers import MoviesController
from ..util import capitalize_movie_name


class RemoveAction(BaseAction):
    action_name = "remove"
    admin = True
    controller = MoviesController()

    async def action(self, msg):
        movie = capitalize_movie_name(self.get_message_data(msg))
        with self.controller.transaction():
            try:
                movie_row = self.controller.get_by_server_and_id(
                    server_id=msg.guild.id, movie=movie
                )
            except pw.DoesNotExist:
                return (msg.channel, f"Movie {movie} has not been suggested")
            self.controller.delete(movie_row)

        return (msg.channel, f"The movie {movie} has been removed from the list.")

    @property
    def help_text(self):
        return "Removes the specified movie from the suggestions list."

    @property
    def help_options(self):
        return ["[movie name]"]
