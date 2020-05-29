from . import BaseAction
from ..db.controllers import MoviesController, ServerController
from ..util import cleanup_messages


class SetIMDBId(BaseAction):
    action_name = "set_imdb_id"
    admin = False
    controller = MoviesController()
    server_controller = ServerController()

    async def action(self, msg):
        server_id = msg.guild.id
        server_row = self.server_controller.get_by_id(server_id)
        message_timeout = server_row.message_timeout
        imdb_id, movie_name = self.get_message_data(msg, data_parts=2)
        updated_rows = self.controller.update_imdb_id(server_id, movie_name, imdb_id)

        if updated_rows == 1:
            server_msg = await msg.channel.send(
                f"Movie {movie_name} has been updated to imdb ID {imdb_id}"
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
        elif updated_rows == 0:
            server_msg = await msg.channel.send(
                f"Unable to update IMDB id for {movie_name}"
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
        else:
            server_msg = await msg.channel.send(
                f"Movie {movie_name} updated multiple entries to IMDB id {imdb_id}"
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)

    @property
    def help_text(self):
        return "Overrides the automatically found IMDB id for a movie suggestion with the given IMDB id"

    @property
    def help_options(self):
        return ["[imdb id] [movie_name]"]
