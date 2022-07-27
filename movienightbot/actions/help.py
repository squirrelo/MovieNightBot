import logging
from typing import Optional

import discord

from . import BaseAction
from ..db.controllers import ServerController


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
            logger.debug(f"user is an admin, showing admin help")
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
                await msg.channel.send(
                    content=content_data, embed=embed_data, delete_after=60
                )
            else:
                raise

    async def action(self, msg: discord.Message):
        action_name = self.get_message_data(msg)
        server_role = self.controller.get_by_id(msg.guild.id).admin_role
        user_roles = {r.name for r in msg.author.roles}
        logger.debug(
            f"Helping user {msg.author.nick} with roles {user_roles} against {server_role}"
        )
        
        if not action_name:
            embed_data = self._build_help_embed_general(server_role in user_roles)
        else:
            embed_data = self._build_help_embed_arg(action_name)
        await self._safe_private_message(msg, None, embed_data)


    @property
    def help_text(self):
        return "DMs the sender of the command this exact message. Now that's meta!"

    @property
    def help_options(self):
        return ["[command_name]"]
