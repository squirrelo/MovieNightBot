import pytest
import discord.ext.test as test


from movienightbot.application import client as BotClient, _server_controller
from movienightbot.config import Config
from movienightbot.db import initialize_db


@pytest.fixture
def client(event_loop):

    bconfig = Config("unused_token", "sqlite:///:memory:")
    bconfig.message_identifier = "m!"
    bconfig.port = 8000
    bconfig.base_url = f"http://localhost:{bconfig.port}"

    bclient = BotClient
    bclient.loop = event_loop
    bclient.config = bconfig
    initialize_db(bconfig.db_url)

    test.configure(bclient, num_guilds=1, num_members=3)

    guild = bclient.guilds[0]
    guild_data = {"id": guild.id, "channel": guild.text_channels[0].id}
    _server_controller.create(guild_data)

    return bclient


@pytest.fixture(autouse=True)
async def cleanup():
    yield
    await test.empty_queue()


def pytest_sessionfinish(session, exitstatus):
    """Code to execute after all tests."""

    # This would have cleaned up the testing db but it is left open forever,
    # meaning we should just use bash and delete post pytest...
    #
    # try:
    #     os.remove(_TEST_SQLITE_FILE)
    # except Exception as e:
    #     print("\nError removing SQLite file:  ", _TEST_SQLITE_FILE)
    #     print(e)
