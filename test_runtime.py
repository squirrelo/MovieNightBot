import discord.ext.test as dpytest
import pytest

"""
m!block_suggestions
m!cancel_vote
m!check_movie_names
m!cleanup
m!end_vote
m!help
m!movie_option_count
m!remove
m!server_settings
m!set_admin
m!set_imdb_id
m!set_message_timeout
m!set_movie_channel
m!set_movie_time
m!set_watched
m!start_vote
m!suggest
m!suggested
m!tie_option
m!unwatch
m!user_vote_count
m!watched
"""

_TEST_SQLITE_FILE = "/testing_db.sqlite"


@pytest.fixture
def client(event_loop):
    from movienightbot.application import client, _server_controller
    from movienightbot.config import Config
    from movienightbot.db import initialize_db

    bconfig = Config("", f"sqlite://{_TEST_SQLITE_FILE}")
    bconfig.message_identifier = "m!"
    bconfig.port = 8000
    bconfig.base_url = f"http://localhost:{bconfig.port}/"

    client.config = bconfig
    initialize_db(bconfig.db_url)

    dpytest.configure(client)

    guild = client.guilds[0]
    guild_data = {"id": guild.id, "channel": guild.text_channels[0].id}
    _server_controller.create(guild_data)

    return client


@pytest.mark.asyncio
async def test_bot(client):
    # print("Post Configure Data: ")
    # print(dpytest.get_config())

    await dpytest.message("m!suggest The Land Before Time")
    dpytest.verify_message(
        "Your suggestion of The Land Before Time () has been added to the list."
    )
