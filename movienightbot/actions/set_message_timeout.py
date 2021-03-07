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
            return (msg.channel, f"Must send an number, got {timeout}")
        if timeout < 0:
            return (msg.channel, f"Timeout value must be >= 0, got {timeout}")
        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.message_timeout = timeout
            self.controller.update(server_row)
        return (msg.channel, f"Message timeout updated to {timeout} seconds")

    @property
    def help_text(self):
        return "Sets how long before the suggestion messages are deleted, in seconds. Set to 0 to not delete them."

    @property
    def help_options(self):
        return ["###"]
