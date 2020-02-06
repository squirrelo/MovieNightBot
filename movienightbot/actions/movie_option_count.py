import peewee as pw

from . import BaseAction
from ..db.controllers import ServerController


class MovieOptionCountAction(BaseAction):
    action_name = "movie_option_count"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        num_movies = self.get_message_data(msg)
        num_movies = int(num_movies)
        if num_movies < 1:
            await msg.channel.send(
                f"Failed to update: Number of movies per vote must be > 0"
            )
            return

        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.num_movies_per_vote = int(num_movies)
            self.controller.update(server_row)
        await msg.channel.send(f"Number of movies per vote updated to {num_movies}")

    @property
    def help_text(self):
        return "Sets the number of movies that will show up on a vote."
