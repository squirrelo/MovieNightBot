from . import BaseAction
from ..db.controllers import ServerController


class SetAdminRoleAction(BaseAction):
    action_name = "imdb_tv_shows"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        toggle_value = self.get_message_data(msg)
        if not toggle_value:
            await msg.channel.send(
                f"Must give value of on or off for imdb_tv_shows command"
            )
            return

        toggle_value = toggle_value.lower()
        if toggle_value == "on":
            allow_tv_shows = True
        elif toggle_value == "off":
            allow_tv_shows = False
        else:
            await msg.channel.send(
                f"Unknown value given. Value must be on or off, got {toggle_value}."
            )
            return

        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.allow_tv_shows = allow_tv_shows
            self.controller.update(server_row)
        await msg.channel.send(f"Allow IMDB tv show search turned {toggle_value}")

    @property
    def help_text(self):
        return "Toggles whether to allow tv shows in the IMDB search results (on) or not (off)."

    @property
    def help_options(self):
        return ["(on|off)"]
