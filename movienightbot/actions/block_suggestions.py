import re

from . import BaseAction
from ..db.controllers import ServerController


class SetMovieTimeAction(BaseAction):
    action_name = "block_suggestions"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        option = self.get_message_data(msg)
        if option == "on":
            block = True
            suggestions_text = "disallowed"
        elif option == "off":
            block = False
            suggestions_text = "allowed"
        else:
            await msg.channel.send(f'Unknown option for block_suggestions: `{option}`')
        server_row = self.controller.get_by_id(msg.guild.id)
        server_row.block_suggestions = block
        self.controller.update(server_row)
        await msg.channel.send(f'Server suggestions are now {suggestions_text}')


    @property
    def help_text(self):
        return (
            "Toggles allowing suggestions. Send `on` to allow, `off` to disallow"
        )
