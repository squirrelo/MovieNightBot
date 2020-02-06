import logging

import discord

from .actions import KNOWN_ACTIONS, unknown_default_action
from .util import build_vote_embed
from .db.controllers import (
    ServerController,
    VoteController,
    UserVoteController,
    MovieVoteController,
)

client = discord.Client()
_server_controller = ServerController()
_vote_controller = VoteController()
_movie_vote_controller = MovieVoteController()
_user_vote_controller = UserVoteController()

logger = logging.getLogger("movienightbot")


@client.event
async def on_ready():
    print(f"Logged in as user {client.user}")
    logger.info(f"Logged in as user {client.user}")
    await client.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="Tracking your shitty movie taste"),
    )


@client.event
async def on_guild_join(guild: discord.Guild):
    guild_data = {"id": guild.id, "channel": guild.text_channels[0]}
    _server_controller.create(**guild_data)
    logger.info(f"Registered on new server {guild.name}")


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
    await action(message)


def is_vote_message(server_id: int, message_id: int) -> bool:
    vote_row = _vote_controller.get_vote_for_server(server_id)
    if not vote_row:
        # no vote going on so can never be the vote row
        return False
    return vote_row.message_id == message_id


async def reset_emoji(emoji: str, message: discord.message, user: discord.User):
    raise NotImplementedError


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    message = reaction.message
    server_id = message.guild.id
    emoji = reaction.emoji
    if not is_vote_message(server_id, message.id):
        return

    # Check if user reset votes, and do that if so
    if emoji == ":arrows_counterclockwise:":
        _user_vote_controller.reset_user_votes(server_id, user.id)
        return
    # Check if user requested end of voting, and do that if so
    elif emoji == ":stop_sign:":
        KNOWN_ACTIONS["end_vote"](message)
        return
    with _movie_vote_controller.transaction():
        movie_vote = _movie_vote_controller.convert_emoji(server_id, emoji)
        _user_vote_controller.register_vote(user.id, movie_vote)

    # Update the vote message
    with _movie_vote_controller.transaction():
        embed = build_vote_embed(server_id)
        await message.edit(content=None, embed=embed, supress=False)


@client.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    message = reaction.message
    server_id = message.guild.id
    emoji = reaction.emoji
    if not is_vote_message(server_id, message.id):
        return
    with _movie_vote_controller.transaction():
        movie_vote = _movie_vote_controller.convert_emoji(server_id, emoji)
        _user_vote_controller.remove_vote(user.id, movie_vote)

        # Update the vote message
        embed = build_vote_embed(server_id)
        await message.edit(content=None, embed=embed, supress=False)
