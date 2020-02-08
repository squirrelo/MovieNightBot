import discord

from . import BaseAction
from ..db.controllers import ServerController


class HelpAction(BaseAction):
    action_name = "help"
    guild_only = False
    controller = ServerController()

    def _build_help_embed(self, server_id: int) -> discord.Embed:
        from . import KNOWN_ACTIONS
        from ..application import client
        server_role = self.controller.get_by_id(server_id).admin_role
        admin_mark = ":no_entry:"
        embed = discord.Embed(
            title="Help Commands",
            description=f"I heard you asked for some help. We all need some from time to time, so here it is."
            f"Commands marked with {admin_mark} require the user to be a server admin or have the role `{server_role}`",
        )
        for action in sorted(KNOWN_ACTIONS):
            cls = KNOWN_ACTIONS[action]
            admin_cls = admin_mark if cls.admin else ""
            embed.add_field(
                name=f"{client.config.message_identifier}{action}",
                value=admin_cls + cls.help_text,
                inline=False,
            )
        return embed

    async def action(self, msg):
        await msg.author.send(content=None, embed=self._build_help_embed(msg.guild.id))

    @property
    def help_text(self):
        return "DMs the sender of the command this exact message. Now that's meta!"
