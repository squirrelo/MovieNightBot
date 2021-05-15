from . import BaseAction
from ..db.controllers import ServerController


class SetAdminRoleAction(BaseAction):
    action_name = "imdb_tv_shows"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        toggle_value = self.get_message_data(msg)
        if toggle_value.lower() == "on":
            toggle_value = True
        elif toggle_value.lower() == "off":
            toggle_value = False
        else:
            await msg.channel.send(
                f"Unknown value given. Value must be on or off, got {toggle_value}."
            )
            return

        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.allow_tv_shows = toggle_value
            self.controller.update(server_row)
        await msg.channel.send(f"Allow IMDB tv show search set to {toggle_value}")

    @property
    def help_text(self):
        return "Toggles whether to allow tv shows in the IMDB search results (on) or not (off)."

    @property
    def help_options(self):
        return ["(on|off)"]
