from typing import Union

import discord

from . import BaseAction
from ..util import cleanup_messages


class CleanupAction(BaseAction):
    action_name = "cleanup"
    admin = True

    async def clear_channel(
        self, channel: Union[discord.DMChannel, discord.GroupChannel], max_messages: int
    ):
        """Clear all messages targeted at bot commands or from the bot from a channel"""
        from ..application import client

        message_identifier = client.config.message_identifier
        messages = []
        for msg in channel.history(limit=max_messages):
            if (
                msg.content.startswith(message_identifier)
                or msg.author.id == client.user.id
            ):
                messages.append(msg)
        await cleanup_messages(messages, 0)

    async def action(self, msg):
        await self.clear_channel(msg.channel, 2000)

    @property
    def help_text(self):
        return "Removes all bot commands and messages in the current server message channel"
