import peewee as pw

from . import BaseAction
from ..db.controllers import MoviesController, ServerController
from ..util import check_imdb, cleanup_messages


class SuggestAction(BaseAction):
    action_name = "suggest"
    controller = MoviesController()
    server_controller = ServerController()
    message_delete_sec_delay = 10

    async def action(self, msg):
        server_id = msg.guild.id
        server_row = self.server_controller.get_by_id(server_id)
        if server_row.block_suggestions:
            server_msg = await msg.channel.send(
                "Suggestions are currently disabled on the server"
            )
            await cleanup_messages(
                [msg, server_msg], sec_delay=self.message_delete_sec_delay
            )
            return
        suggestion = self.get_message_data(msg)
        suggestion = suggestion.title()

        if server_row.check_movie_names and not check_imdb(suggestion):
            server_msg = await msg.channel.send(
                "Could not find the title you suggested in IMDb."
            )
            await cleanup_messages(
                [msg, server_msg], sec_delay=self.message_delete_sec_delay
            )
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
            await cleanup_messages(
                [msg, server_msg], sec_delay=self.message_delete_sec_delay
            )
            return
        server_msg = await msg.channel.send(
            f"Your suggestion of {suggestion} has been added to the list."
        )
        await cleanup_messages(
            [msg, server_msg], sec_delay=self.message_delete_sec_delay
        )

    @property
    def help_text(self):
        return (
            "Adds the supplied movie to the suggestions list. There is a chance this movie will now "
            "show up on future votes"
        )

    @property
    def help_options(self):
        return ["[movie name]"]
