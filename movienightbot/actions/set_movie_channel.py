from . import BaseAction
from ..db.controllers import ServerController


class SetMovieChannelAction(BaseAction):
    action_name = "set_channel"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        channel = self.get_message_data(msg)
        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            channels = {c.name: c.id for c in msg.guild.text_channels}
            if channel not in channels:
                await msg.channel.send(
                    f"Failed update: unknown channel {channel} given."
                )
                return
            server_row.channel = channels[channel]
            self.controller.update(server_row)
        await msg.channel.send(f"Bot channel updated to {channel}")

    @property
    def help_text(self):
        return "Sets the channel the bot wil listen in. Default is top text channel in the server"

    @property
    def help_options(self):
        return ["[channel]"]
