import re

from . import BaseAction
from ..db.controllers import ServerController


class SetMovieTimeAction(BaseAction):
    action_name = "set_movie_time"
    admin = True
    controller = ServerController()
    time_regex = re.compile("^\d{1,2}:\d{2}$")

    async def action(self, msg):
        movie_time = self.get_message_data(msg)
        if not self.time_regex.search(movie_time):
            await msg.channel.send(
                f"Movie time given in invalid format. Must be `HH:MM`"
            )
            return
        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.movie_time = movie_time
            self.controller.update(server_row)
        await msg.channel.send(f"Movie time updated to {movie_time} UTC")

    @property
    def help_text(self):
        return (
            "Sets the time when the movie will be watched. Format must be HH:MM\n"
            "The time is in UTC time zone, so convert accordingly. Valid range is 0 - 23\n"
            "This time shows at the bottom of the vote embed."
        )

    @property
    def help_options(self):
        return ["HH:MM"]
