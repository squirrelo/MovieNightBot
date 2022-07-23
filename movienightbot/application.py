import logging

import discord
import peewee as pw

from .actions import KNOWN_ACTIONS, unknown_default_action
from .util import build_vote_embed, emojis_unicode, emojis_text
from .db.controllers import (
    ServerController,
    VoteController,
    UserVoteController,
    MovieVoteController,
)

client = discord.Client(intents=discord.Intents.all())
_server_controller = ServerController()
_vote_controller = VoteController()
_movie_vote_controller = MovieVoteController()
_user_vote_controller = UserVoteController()

logger = logging.getLogger("movienightbot")

client._cached_app_info = None


async def generate_invite_link(permissions=discord.Permissions(388160), guild=None):
    if client._cached_app_info is None:
        logger.info("Caching App Info...")
        client._cached_app_info = await client.application_info()
    return discord.utils.oauth_url(
        client._cached_app_info.id, permissions=permissions, guild=guild
    )


@client.event
async def on_ready():
    print(f"Logged in as user {client.user}")
    logger.info(f"Logged in as user {client.user}")

    auth_url = await generate_invite_link()
    logger.info(f"Bot Invite URL:  {auth_url}")

    await client.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="Tracking your shitty movie taste"),
    )


def register_guild(guild: discord.Guild):
    guild_data = {"id": guild.id, "channel": guild.text_channels[0].id}
    _server_controller.create(guild_data)
    logger.info(f"Registered on new server {guild.name}")


@client.event
async def on_guild_join(guild: discord.Guild):
    register_guild(guild)


@client.event
async def on_guild_remove(guild: discord.Guild):
    with _server_controller.transaction():
        server_row = _server_controller.get_by_id(guild.id)
        _server_controller.delete(server_row, recursive=True)
    logger.info(f"Removed from server {guild.name}")


@client.event
async def on_message(message: discord.message):
    message_identifier = client.config.message_identifier
    if not message.content.startswith(message_identifier):
        # Ignore anything that doesnt start with our expected command identifier
        return

    message_info = message.content.rstrip().split(" ")
    # Strip off the message identifier to find what our action should be
    command = message_info[0][len(message_identifier) :]

    try:
        action = KNOWN_ACTIONS[command]
    except KeyError:
        await unknown_default_action(message, command)
        return

    # Make sure server is registered, and register if not (#55)
    try:
        _server_controller.get_by_id(message.guild.id)
    except pw.DoesNotExist:
        register_guild(message.guild)

    await action(message)


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
    is_message = (vote_row.message_id == message_id) and (
        vote_row.channel_id == channel_id
    )
    logger.debug(
        "Vote DB channel and message: {} {} >> Sent channel and message: {} {} >> {}".format(
            vote_row.channel_id, vote_row.message_id, channel_id, message_id, is_message
        )
    )
    return is_message


async def parse_reaction(payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await client.fetch_user(payload.user_id)
    emoji = emojis_unicode.get(payload.emoji.name, None)
    logger.debug(
        "raw emoji sent: {} {}  >> {}".format(
            type(payload.emoji.name), type(payload.emoji), emoji
        )
    )
    # Ignore if emojis coming from this bot
    if user.id == client.user.id:
        logger.debug("emoji coming from self")
        emoji = None
    return message, user, channel.guild.id, emoji


@client.event
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
        await KNOWN_ACTIONS["end_vote"](message)
        return
    with _movie_vote_controller.transaction():
        logger.info(
            f"Registering emoji vote {emoji} for {user.id} on {message.guild.name}"
        )
        movie_vote = _movie_vote_controller.convert_emoji(server_id, emoji)
        logger.debug(f"Got movie vote {movie_vote.id}")
        _user_vote_controller.register_vote(user.id, user.display_name, movie_vote)

    # Update the vote message
    embed = build_vote_embed(server_id)
    await message.edit(content=None, embed=embed, supress=False)


@client.event
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
