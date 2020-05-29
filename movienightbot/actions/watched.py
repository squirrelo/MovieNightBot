from . import BaseAction


class WatchedAction(BaseAction):
    action_name = "watched"

    async def action(self, msg):
        from ..application import client

        await msg.channel.send(
            f"Watched movies can be found at {client.config.base_url}/watched/{msg.guild.id}"
        )

    @property
    def help_text(self):
        return "Lists all movies that have been watched."
