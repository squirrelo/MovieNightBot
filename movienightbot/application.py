import logging
from pathlib import Path

import discord
from discord.ext import commands
import peewee as pw

from .util import build_vote_embed, emojis_text, emojis_unicode, is_admin, generate_invite_link
from .db.controllers import (
    ServerController,
    VoteController,
    UserVoteController,
    MovieVoteController,
)

class MovieNightBot(commands.Bot):
    _server_controller = ServerController()
    _vote_controller = VoteController()
    _movie_vote_controller = MovieVoteController()
    _user_vote_controller = UserVoteController()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("movienightbot")

    def _is_vote_message(self, server_id: int, channel_id: int, message_id: int) -> bool:
        try:
            vote_row = self._vote_controller.get_by_id(server_id)
            self.logger.debug("vote_row: {}".format(vote_row))
        except pw.DoesNotExist:
            self.logger.debug("No vote found for server {}".format(server_id))
            return False
        if not vote_row:
            # no vote going on so can never be the vote row
            self.logger.debug("Empty vote found for server {}".format(server_id))
            return False
        is_message = (vote_row.message_id == message_id) and (vote_row.channel_id == channel_id)
        self.logger.debug(
            "Vote DB channel and message: {} {} >> Sent channel and message: {} {} >> {}".format(
                vote_row.channel_id, vote_row.message_id, channel_id, message_id, is_message
            )
        )
        return is_message

    async def _parse_reaction(self, payload):
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await bot.fetch_user(payload.user_id)
        emoji = emojis_unicode.get(payload.emoji.name, None)
        self.logger.debug("raw emoji sent: {} {}  >> {}".format(type(payload.emoji.name), type(payload.emoji), emoji))
        # Ignore if emojis coming from this bot
        if user.id == bot.user.id:
            self.logger.debug("emoji coming from self")
            emoji = None
        return message, user, channel.guild.id, emoji

    async def setup_hook(self):
        commands_dir = Path(__file__).parent.joinpath("commands")
        commands = []
        for file in commands_dir.iterdir():
            if file.is_dir() or file.name.startswith("__") or not file.name.endswith(".py"):
                continue
            command = f"movienightbot.commands.{file.stem}"
            await self.load_extension(command)
            commands.append(command)
        self.logger.debug("loaded commands: %s", ", ".join(sorted(commands)))

    async def on_ready(self):
        self.logger.info(f"Logged in as user {bot.user}")

        auth_url = await generate_invite_link()
        self.logger.info(f"Bot Invite URL:  {auth_url}")

        synced = await bot.tree.sync()
        self.logger.info(f"Synced {len(synced)} commands")

        await bot.change_presence(
            status=discord.Status.idle,
            activity=discord.Game(name="Tracking your shitty movie taste"),
        )

    async def on_guild_join(self, guild: discord.Guild):
        guild_data = {"id": guild.id}
        self._server_controller.create(guild_data)
        self.logger.info(f"Registered on new server {guild.name}")

    async def on_guild_remove(self, guild: discord.Guild):
        with self._server_controller.transaction():
            server_row = self._server_controller.get_by_id(guild.id)
            self._server_controller.delete(server_row, recursive=True)
        self.logger.info(f"Removed from server {guild.name}")

    async def on_raw_reaction_add(self, payload):
        message, user, server_id, emoji = await self._parse_reaction(payload)
        self.logger.debug("Reaction {} added to server {}", emoji, server_id)
        if emoji is None or not self._is_vote_message(server_id, message.channel.id, message.id):
            self.logger.debug("emoji from self or not vote message")
            return
        # Check if user reset votes, and do that if so
        if emoji == ":arrows_counterclockwise:":
            movie_votes = self._user_vote_controller.reset_user_votes(server_id, user.id)
            # Reset the user's emojis for the movies they voted for
            for movie in movie_votes:
                await message.remove_reaction(emojis_text[movie.emoji], user)
            await message.remove_reaction(emojis_text[":arrows_counterclockwise:"], user)
            return

        with self._movie_vote_controller.transaction():
            try:
                movie_vote = self._movie_vote_controller.convert_emoji(server_id, emoji)
            except pw.DoesNotExist:
                # Unknown emoji, so nothing to do
                self.logger.debug("Add vote: Unknkown emoji {} sent", emoji)
                return
            self.logger.debug("Got movie vote {}", movie_vote.id)
            self.logger.info(f"Registering emoji vote {emoji} for {user.id} on {message.guild.name}")
            self._user_vote_controller.register_vote(user.id, user.display_name, movie_vote)

        # Update the vote message
        embed = build_vote_embed(server_id)
        await message.edit(content=None, embed=embed, suppress=False)

    async def on_raw_reaction_remove(self, payload):
        message, user, server_id, emoji = await self._parse_reaction(payload)
        if emoji is None or not self._is_vote_message(server_id, message.channel.id, message.id):
            self.logger.debug("emoji not vote message")
            return

        with self._movie_vote_controller.transaction():
            try:
                movie_vote = self._movie_vote_controller.convert_emoji(server_id, emoji)
            except pw.DoesNotExist:
                # Unknown emoji, so nothing to do
                self.logger.debug(f"Remove Vote: Unknkown emoji {emoji} sent")
                return
            self._user_vote_controller.remove_vote(user.id, movie_vote)

        # Update the vote message
        self.logger.info(f"Removing emoji vote {emoji} for {user.id} on {message.guild.name}")
        embed = build_vote_embed(server_id)
        await message.edit(content=None, embed=embed)


bot = MovieNightBot(command_prefix="m!", intents=discord.Intents.default())


# One built-in command to force commands sync, others must be extensions
@bot.command(description="[ADMIN COMMAND] force resync of commands.")
@discord.app_commands.check(is_admin)
async def sync(interaction: discord.Interaction):
    synced = await bot.tree.sync(guild=interaction.guild)
    await interaction.response.send_message(f"Synced {len(synced)} commands", ephemeral=True)
