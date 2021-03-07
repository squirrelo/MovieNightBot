import discord

from . import BaseAction
from ..db.controllers import ServerController


class ServerSettingsAction(BaseAction):
    action_name = "server_settings"
    admin = True
    controller = ServerController()

    def format_embed(self, server_id: int) -> discord.Embed:
        from ..application import client

        ignore_attrs = {"id"}
        server_row = self.controller.get_by_id(server_id)
        # Replace channel ID with the name for ease of interpretation
        server_row.channel = client.get_channel(server_row.channel)
        guild_name = client.get_guild(server_row.id)
        embed = discord.Embed(
            title=f"{guild_name} Settings",
            description=f"Current settings for server `{guild_name}`",
        )
        for attr, value in server_row.__data__.items():
            if attr in ignore_attrs:
                continue
            embed.add_field(name=attr, value=value, inline=False)
        return embed

    async def action(self, msg):
        embed_data = self.format_embed(msg.guild.id)
        return (msg.author, {"content": None, "embed": embed_data})

    @property
    def help_text(self):
        return "View the current server settings"
