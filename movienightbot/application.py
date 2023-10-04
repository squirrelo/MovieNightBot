import logging
from pathlib import Path

import discord
from discord.ext import commands
import peewee as pw

from .commands.end_vote import end_vote_task
from .util import build_vote_embed, emojis_unicode, emojis_text
from .db.controllers import (
    ServerController,
    VoteController,
    UserVoteController,
    MovieVoteController,
)


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="m!", intents=intents)
_server_controller = ServerController()
_vote_controller = VoteController()
_movie_vote_controller = MovieVoteController()
_user_vote_controller = UserVoteController()

logger = logging.getLogger("movienightbot")

bot._cached_app_info = None


async def generate_invite_link(permissions=discord.Permissions(403727019072), guild=None):
    if bot._cached_app_info is None:
        logger.info("Caching App Info...")
        bot._cached_app_info = await bot.application_info()
    args = dict(bot_id=bot._cached_app_info.id, permissions=permissions)
    # Need to do it this way so we don't send guild property at all if it's None. Yay py-cord limitations.
    if guild is not None:
        args["guild"] = guild
    return discord.utils.oauth_url(**args)


@bot.event
async def on_ready():
    print(f"Logged in as user {bot.user}")
    logger.info(f"Logged in as user {bot.user}")

    auth_url = await generate_invite_link()
    logger.info(f"Bot Invite URL:  {auth_url}")

    for file in Path("commands").iterdir():
        if file.is_dir() or file.name.startswith("__") or not file.name.endswith(".py"):
            continue
        await bot.load_extension(f"commands.{file.stem}")

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands")

    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="Tracking your shitty movie taste"),
    )


def register_guild(guild: discord.Guild):
    guild_data = {"id": guild.id, "channel": guild.text_channels[0].id}
    _server_controller.create(guild_data)
    logger.info(f"Registered on new server {guild.name}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    register_guild(guild)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    with _server_controller.transaction():
        server_row = _server_controller.get_by_id(guild.id)
        _server_controller.delete(server_row, recursive=True)
    logger.info(f"Removed from server {guild.name}")


def is_vote_message(server_id: int, channel_id: int, message_id: int) -> bool:
    try:
        vote_row = _vote_controller.get_by_id(server_id)
        logger.debug("vote_row: {}".format(vote_row))
    except pw.DoesNotExist:
        logger.debug("No vote found for server {}".format(server_id))
        return False
    if not vote_row:
        # no vote going on so can never be the vote row
        logger.debug("Empty vote found for server {}".format(server_id))
        return False
    is_message = (vote_row.message_id == message_id) and (vote_row.channel_id == channel_id)
    logger.debug(
        "Vote DB channel and message: {} {} >> Sent channel and message: {} {} >> {}".format(
            vote_row.channel_id, vote_row.message_id, channel_id, message_id, is_message
        )
    )
    return is_message


async def parse_reaction(payload):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    emoji = emojis_unicode.get(payload.emoji.name, None)
    logger.debug("raw emoji sent: {} {}  >> {}".format(type(payload.emoji.name), type(payload.emoji), emoji))
    # Ignore if emojis coming from this bot
    if user.id == bot.user.id:
        logger.debug("emoji coming from self")
        emoji = None
    return message, user, channel.guild.id, emoji


@bot.event
async def on_raw_reaction_add(payload):
    message, user, server_id, emoji = await parse_reaction(payload)
    logger.debug("Reaction {} added to server {}".format(emoji, server_id))
    if emoji is None or not is_vote_message(server_id, message.channel.id, message.id):
        logger.debug("emoji from self or not vote message")
        return
    # Check if user reset votes, and do that if so
    if emoji == ":arrows_counterclockwise:":
        movie_votes = _user_vote_controller.reset_user_votes(server_id, user.id)
        # Reset the user's emojis for the movies they voted for
        for movie in movie_votes:
            await message.remove_reaction(emojis_text[movie.emoji], user)
        await message.remove_reaction(emojis_text[":arrows_counterclockwise:"], user)
        return
    # Check if user requested end of voting, and do that if so
    elif emoji == ":octagonal_sign:":
        await end_vote_task(message)
        return
    with _movie_vote_controller.transaction():
        logger.info(f"Registering emoji vote {emoji} for {user.id} on {message.guild.name}")
        movie_vote = _movie_vote_controller.convert_emoji(server_id, emoji)
        logger.debug(f"Got movie vote {movie_vote.id}")
        _user_vote_controller.register_vote(user.id, user.display_name, movie_vote)

    # Update the vote message
    embed = build_vote_embed(server_id)
    await message.edit(content=None, embed=embed, suppress=False)


@bot.event
async def on_raw_reaction_remove(payload):
    message, user, server_id, emoji = await parse_reaction(payload)
    if emoji is None or not is_vote_message(server_id, message.channel.id, message.id):
        logger.debug("emoji not vote message")
        return
    logger.info(f"Removing emoji vote {emoji} for {user.id} on {message.guild.name}")
    with _movie_vote_controller.transaction():
        movie_vote = _movie_vote_controller.convert_emoji(server_id, emoji)
        _user_vote_controller.remove_vote(user.id, movie_vote)

    # Update the vote message
    embed = build_vote_embed(server_id)
    await message.edit(content=None, embed=embed, supress=False)
