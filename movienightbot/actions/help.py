import discord

from . import BaseAction


class HelpAction(BaseAction):
    action_name = "help"
    guild_only = False

    def _build_help_embed(self) -> discord.Embed:
        from . import KNOWN_ACTIONS
        from ..application import client

        admin_mark = ":no_entry:"
        embed = discord.Embed(
            title="Help Commands",
            description=f"I heard you asked for some help. We all need some from time to time, so here it is."
            f"Commands marked with {admin_mark} require the user to be a server admin or have the role `Movie Master`, "
            f"unless the server owner has changed it.",
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
        await msg.author.send(content=None, embed=self._build_help_embed())

    @property
    def help_text(self):
        return "DMs the sender of the command this exact message. Now that's meta!"
