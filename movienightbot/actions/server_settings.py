import discord

from . import BaseAction
from ..db.controllers import ServerController


class SetMovieTimeAction(BaseAction):
    action_name = "server_settings"
    admin = True
    controller = ServerController()

    def format_embed(self, server_id: int) -> discord.Embed:
        from ..application import client

        server_row = self.controller.get_by_id(server_id)
        # Replace channel ID with the name for ease of interpretation
        server_row.channel_id = client.get_channel(server_row.channel_id)
        embed = discord.Embed(
            title="Server Settings", description="Current settings for your server"
        )
        for attr, value in vars(server_row).items():
            embed.add_field(name=f"{attr}: {value}", inline=False)
        return embed

    async def action(self, msg):
        embed_data = self.format_embed(msg.guild.id)
        await msg.author.send(content=None, embed=embed_data)

    @property
    def help_text(self):
        return "View the current server settings"
