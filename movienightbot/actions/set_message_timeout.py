from . import BaseAction
from ..db.controllers import ServerController


class SetMessageTimeoutAction(BaseAction):
    action_name = "set_message_timeout"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        timeout = self.get_message_data(msg)
        try:
            timeout = int(timeout)
        except ValueError:
            await msg.channel.send(f"Must send an number, got {timeout}")
            return
        if timeout < 0:
            await msg.channel.send(f"Timeout value must be >= 0, got {timeout}")
            return
        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.message_timeout = timeout
            self.controller.update(server_row)
        await msg.channel.send(f"Message timeout updated to {timeout} seconds")

    @property
    def help_text(self):
        return "Sets how long before the suggestion messages are deleted, in seconds. Set to 0 to not delete them."

    @property
    def help_options(self):
        return ["###"]
