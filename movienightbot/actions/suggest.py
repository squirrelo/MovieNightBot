import peewee as pw

from . import BaseAction
from ..db.controllers import MoviesController, ServerController
from ..util import check_imdb, cleanup_messages


class SuggestAction(BaseAction):
    action_name = "suggest"
    controller = MoviesController()
    server_controller = ServerController()

    async def action(self, msg):
        server_id = msg.guild.id
        server_row = self.server_controller.get_by_id(server_id)
        message_timeout = server_row.message_timeout
        if server_row.block_suggestions:
            server_msg = await msg.channel.send(
                "Suggestions are currently disabled on the server"
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
            return
        suggestion = self.get_message_data(msg)
        suggestion = suggestion.title()

        if server_row.check_movie_names and not check_imdb(suggestion):
            server_msg = await msg.channel.send(
                "Could not find the title you suggested in IMDb."
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
            return

        movie_data = {
            "server": server_id,
            "movie_name": suggestion,
            "suggested_by": msg.author.name,
        }
        try:
            self.controller.create(movie_data)
        except pw.IntegrityError:
            server_msg = await msg.channel.send(
                f"{suggestion} has already been suggested in this server."
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
            return
        server_msg = await msg.channel.send(
            f"Your suggestion of {suggestion} has been added to the list."
        )
        if message_timeout > 0:
            await cleanup_messages([msg, server_msg], sec_delay=message_timeout)

    @property
    def help_text(self):
        return (
            "Adds the supplied movie to the suggestions list. There is a chance this movie will now "
            "show up on future votes"
        )

    @property
    def help_options(self):
        return ["[movie name]"]
