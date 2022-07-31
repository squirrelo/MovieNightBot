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

    def _build_help_embed_general(self, is_admin: bool) -> discord.Embed:
        from . import KNOWN_ACTIONS
        from ..application import client

        embed = discord.Embed(
            title="Help & Commands",
            description="Here is a list of commands available to you.",
        )
        embed.add_field(
            name="Command usage:",
            value=f"`{client.config.message_identifier}{self.action_name} {' '.join(self.help_options)}`",
            inline=False,
        )
        cmd_list = []
        adm_list = []
        for action in sorted(KNOWN_ACTIONS):
            cls = KNOWN_ACTIONS[action]
            if cls.admin:
                adm_list.append(action)
            else:
                cmd_list.append(action)

        embed.add_field(
            name="General Commands: ",
            value=f"```{', '.join(cmd_list)}```",
            inline=False,
        )

        if is_admin:
            logger.debug("user is an admin, showing admin help")
            embed.add_field(
                name="Admin Commands: ",
                value=f"```{', '.join(adm_list)}```",
                inline=False,
            )

        return embed

    def _build_help_embed_arg(self, action: str) -> discord.Embed:
        from . import KNOWN_ACTIONS
        from ..application import client

        if action not in KNOWN_ACTIONS:
            embed = discord.Embed(
                title=f"Unknown Command:  {action}",
                description="These are not the commands you are looking for. :wave:",
            )
        else:
            cls = KNOWN_ACTIONS[action]
            embed = discord.Embed(
                title=f"{client.config.message_identifier}{action} {' '.join(cls.help_options)}",
                description=cls.help_text,
            )
        return embed

    def _build_verbose_help_embed(self) -> discord.Embed:
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

    def _build_verbose_admin_help_embed(self) -> discord.Embed:
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
        embeds_data: list[discord.Embed],
    ) -> None:
        try:
            await msg.author.send(content=content_data, embeds=embeds_data)
        except discord.Forbidden as ex:
            # For error/exception codes see: https://discord.com/developers/docs/topics/opcodes-and-status-codes#json
            if ex.code == 50007:  # Cannot Send messages to this user
                thread = await msg.create_thread(name="Help thread")
                await thread.send(content=content_data, embeds=embeds_data)
                await delete_thread(thread, sec_delay=120)
            else:
                raise

    async def action(self, msg: discord.Message):
        action_name = self.get_message_data(msg)
        server_role = self.controller.get_by_id(msg.guild.id).admin_role
        user_roles = {r.name for r in msg.author.roles}
        admin = ""
        if server_role in user_roles:
            admin = "(is admin)"
        logger.debug(
            f"Helping user {msg.author.nick}{admin} with roles {user_roles} against {server_role}"
        )

        embeds_data = []
        if not action_name:
            embeds_data += [self._build_help_embed_general(server_role in user_roles)]
        elif action_name in ["all", "verbose"]:
            embeds_data += [self._build_verbose_help_embed()]
            if server_role in user_roles:
                embeds_data += [self._build_verbose_admin_help_embed()]
        else:
            embeds_data += [self._build_help_embed_arg(action_name)]
        await self._safe_private_message(msg, None, embeds_data)

    @property
    def help_text(self):
        return "DMs the sender of the command this exact message. Now that's meta!"

    @property
    def help_options(self):
        return ["[command_name]"]
