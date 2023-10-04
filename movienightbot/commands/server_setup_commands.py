import logging
import re

import discord
from discord import app_commands
from peewee import DoesNotExist

from movienightbot.util import capitalize_movie_name
from movienightbot.db.controllers import ServerController, MoviesController

logger = logging.getLogger("movienightbot")


class ServerAdmin(app_commands.Group):
    server_controller = ServerController()
    movies_controller = MoviesController()
    time_regex = re.compile(r"^\d{1,2}:\d{2}$")

    @app_commands.command(
        description="Toggles whether to allow tv shows in the IMDB search results (True) or not (False)."
    )
    @app_commands.default_permissions(administrator=True)
    async def imdb_tv_shows(self, interaction: discord.Interaction, allow_tv_shows: bool):
        with self.server_controller.transaction():
            server_row = self.server_controller.get_by_id(interaction.guild.id)
            server_row.allow_tv_shows = allow_tv_shows
            self.server_controller.update(server_row)
        await interaction.response.send_message(f"Allow IMDB tv show search {allow_tv_shows}")

    @app_commands.command(description="Toggles allowing suggestions.")
    @app_commands.default_permissions(administrator=True)
    async def block_suggestions(self, interaction: discord.Interaction, block: bool):
        server_row = self.server_controller.get_by_id(interaction.guild.id)
        server_row.block_suggestions = block
        self.server_controller.update(server_row)
        suggestions_text = "blocked" if block else "unblocked"
        await interaction.response.send_message(f"Server suggestions are now {suggestions_text}")

    @app_commands.command(description="Toggles checking suggestions against IMDB database before adding.")
    @app_commands.default_permissions(administrator=True)
    async def check_movie_names(self, interaction: discord.Interaction, check_names: bool):
        server_row = self.server_controller.get_by_id(interaction.guild.id)
        server_row.check_movie_names = check_names
        self.server_controller.update(server_row)
        option = "on" if check_names else "off"
        await interaction.response.send_message(f"IMDB movie name checks are now {option}")

    @app_commands.command(description="Sets the number of movies that will show up on a vote.")
    @app_commands.default_permissions(administrator=True)
    async def movie_option_count(
        self,
        interaction: discord.Interaction,
        num_movies: app_commands.Range[int, 2, 25],
    ):
        with self.server_controller.transaction():
            server_row = self.server_controller.get_by_id(interaction.guild.id)
            server_row.num_movies_per_vote = int(num_movies)
            self.server_controller.update(server_row)
        await interaction.response.send_message(f"Number of movies per vote updated to {num_movies}")

    @app_commands.command(description="Removes the specified movie from the suggestions list.")
    @app_commands.default_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, movie: str):
        movie = capitalize_movie_name(movie)
        with self.movies_controller.transaction():
            try:
                movie_row = self.movies_controller.get_by_server_and_id(server_id=interaction.guild.id, movie=movie)
            except DoesNotExist:
                await interaction.response.send_message(f"Movie {movie} has not been suggested", ephemeral=True)
                return
            self.movies_controller.delete(movie_row)

        await interaction.response.send_message(f"The movie {movie} has been removed from the list.")

    def _format_server_embed(self, client: discord.Client, server_id: int) -> discord.Embed:
        ignore_attrs = {"id"}
        server_row = self.server_controller.get_by_id(server_id)
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
            if attr.lower() == "movie_time":
                value = str(value) + " UTC"
            embed.add_field(name=attr, value=value, inline=False)
        return embed

    @app_commands.command(description="View the current server settings")
    @app_commands.default_permissions(administrator=True)
    async def server_settings(self, interaction: discord.Interaction):
        embed_data = self._format_server_embed(interaction.client, interaction.guild.id)
        await interaction.response.send_message(content=None, embed=embed_data)

    @app_commands.command(
        description="Sets the role allowed to run admin commands. Server administrators have admin by default"
    )
    @app_commands.default_permissions(administrator=True)
    async def set_admin_role(self, interaction: discord.Interaction, role: str):
        server_roles = [r.name for r in interaction.guild.roles]
        if role not in server_roles:
            await interaction.response.send_message(f"Role not found: {role}.", ephemeral=True)
            return
        with self.server_controller.transaction():
            server_row = self.server_controller.get_by_id(interaction.guild.id)
            server_row.admin_role = role
            self.server_controller.update(server_row)
        await interaction.response.send_message(f"Admin role updated to {role}")

    @app_commands.command(
        description="How long before suggestion messages are deleted, in seconds. Set to 0 to disable."
    )
    @app_commands.default_permissions(administrator=True)
    async def set_message_timeout(
        self,
        interaction: discord.Interaction,
        timeout: app_commands.Range[int, 0, None],
    ):
        with self.server_controller.transaction():
            server_row = self.server_controller.get_by_id(interaction.guild.id)
            server_row.message_timeout = timeout
            self.server_controller.update(server_row)
        await interaction.response.send_message(f"Message timeout updated to {timeout} seconds")

    @app_commands.command(description="Sets the channel the bot wil listen in.")
    @app_commands.default_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction, channel: str):
        with self.server_controller.transaction():
            channels = {c.name: c.id for c in interaction.guild.text_channels}
            if channel not in channels:
                await interaction.response.send_message(
                    f"Failed update: unknown channel {channel} given.", ephemeral=True
                )
                return

            server_row = self.server_controller.get_by_id(interaction.guild.id)
            server_row.channel = channels[channel]
            self.server_controller.update(server_row)
        await interaction.response.send_message(f"Bot channel updated to {channel}")

    @app_commands.command(description="Sets the time when the movie will be watched in 24 hour UTC time.")
    @app_commands.default_permissions(administrator=True)
    async def set_movie_time(self, interaction: discord.Interaction, movie_time: str):
        if not self.time_regex.search(movie_time):
            await interaction.response.send_message(
                "Movie time given in invalid format. Must be `HH:MM`", ephemeral=True
            )
            return
        with self.server_controller.transaction():
            server_row = self.server_controller.get_by_id(interaction.guild.id)
            server_row.movie_time = movie_time
            self.server_controller.update(server_row)
        await interaction.response.send_message(f"Movie time updated to {movie_time} UTC")

    @app_commands.command(
        description="Sets how the bot handles tied votes. `breaker`: revote with ties (default). `random`: new vote"
    )
    @app_commands.default_permissions(administrator=True)
    async def tie_option(self, interaction: discord.Interaction, tie_option: str):
        tie_options = {"breaker", "random"}
        if tie_option not in tie_options:
            await interaction.response.send_message(
                f"Unknown tiebreaker option given: {tie_option}. Must be one of {''.join(tie_options)}",
                ephemeral=True,
            )
            return
        with self.server_controller.transaction():
            server_row = self.server_controller.get_by_id(interaction.guild.id)
            server_row.tie_option = tie_option
            self.server_controller.update(server_row)
        await interaction.response.send_message(f"Tiebreaker updated to {tie_option}")

    @app_commands.command(description="Number of movies a user can vote for.")
    @app_commands.default_permissions(administrator=True)
    async def user_vote_count(
        self,
        interaction: discord.Interaction,
        num_votes_per_user: app_commands.Range[int, 1, 25],
    ):
        with self.server_controller.transaction():
            server_row = self.server_controller.get_by_id(interaction.guild.id)
            if num_votes_per_user > server_row.num_movies_per_vote:
                await interaction.response.send_message(
                    f"Failed to update: Number of votes per user must be <= {server_row.num_movies_per_vote}",
                    ephemeral=True,
                )
                return
            server_row.num_votes_per_user = int(num_votes_per_user)
            self.server_controller.update(server_row)
            await interaction.response.send_message(f"Number of votes per user updated to {num_votes_per_user}")


async def setup(bot):
    bot.tree.add_command(ServerAdmin(name="server", description="Admin commands for MovieNightBot server setup"))
    logger.info("Loaded server commands")
