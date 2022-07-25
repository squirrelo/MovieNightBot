import logging
from typing import Optional

import discord

from . import BaseAction
from ..db.controllers import ServerController
from ..util import delete_thread


logger = logging.getLogger("movienightbot")


class HelpAction(BaseAction):
    action_name = "help"
    guild_only = False
    controller = ServerController()

    def _build_help_embed(self) -> discord.Embed:
        from . import KNOWN_ACTIONS
        from ..application import client

        embed = discord.Embed(
            title="Help Commands",
            description="I heard you asked for some help. We all need some from time to time, so here it is.",
        )
        for action in sorted(KNOWN_ACTIONS):
            cls = KNOWN_ACTIONS[action]
            if cls.admin:
                continue
            embed.add_field(
                name=f"{client.config.message_identifier}{action} {' '.join(cls.help_options)}",
                value=cls.help_text,
                inline=False,
            )
        return embed

    def _build_admin_help_embed(self) -> discord.Embed:
        from . import KNOWN_ACTIONS
        from ..application import client

        embed = discord.Embed(
            title="Admin Help Commands",
            description="Oh look, you're a super special admin. That means you can do this stuff too.",
        )
        for action in sorted(KNOWN_ACTIONS):
            cls = KNOWN_ACTIONS[action]
            if not cls.admin:
                continue
            embed.add_field(
                name=f"{client.config.message_identifier}{action} {' '.join(cls.help_options)}",
                value=cls.help_text,
                inline=False,
            )
        return embed

    async def _safe_private_message(
        self,
        msg: discord.Message,
        content_data: Optional[str],
        embed_data: discord.Embed,
    ) -> None:
        try:
            await msg.author.send(content=content_data, embed=embed_data)
        except discord.Forbidden as ex:
            # For error/exception codes see: https://discord.com/developers/docs/topics/opcodes-and-status-codes#json
            if ex.code == 50007:  # Cannot Send messages to this user
                thread = await msg.create_thread(name="Help thread")
                await thread.send(content=content_data, embed=embed_data)
                await delete_thread(thread, sec_delay=120)
            else:
                raise

    async def action(self, msg: discord.Message):
        embed_data = self._build_help_embed()
        await self._safe_private_message(msg, None, embed_data)
        server_role = self.controller.get_by_id(msg.guild.id).admin_role
        user_roles = {r.name for r in msg.author.roles}
        logger.debug(
            f"Checking user {msg.author.nick} with roles {user_roles} against {server_role}"
        )
        if server_role in user_roles:
            logger.debug(f"user {msg.author.nick} is an admin, showing admin help")
            admin_embed_data = self._build_admin_help_embed()
            await self._safe_private_message(msg, None, admin_embed_data)

    @property
    def help_text(self):
        return "DMs the sender of the command this exact message. Now that's meta!"
