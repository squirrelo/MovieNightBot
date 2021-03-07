from . import BaseAction
from ..db.controllers import ServerController


class CheckMovieNamesAction(BaseAction):
    action_name = "check_movie_names"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        option = self.get_message_data(msg)
        if option == "on":
            check_names = True
        elif option == "off":
            check_names = False
        else:
            return (msg.channel, f"Unknown option for check_movie_names: `{option}`")
        server_row = self.controller.get_by_id(msg.guild.id)
        server_row.check_movie_names = check_names
        self.controller.update(server_row)
        return (msg.channel, f"IMDB movie name checks are now {option}")

    @property
    def help_text(self):
        return (
            "Toggles checking suggestions against IMDB database before adding. "
            "Send `on` to turn on, `off` to turn off"
        )

    @property
    def help_options(self):
        return ["(on|off)"]
