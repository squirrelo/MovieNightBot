import discord
import discord.ext.test as test
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
m!set_admin_role
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


unknown_default_action:
    f"Unknown command {command} given, try reading the tutorial at `m!help` "
    f"to see what commands are available!"

guild_only:
    "You can't do this command from a DM!"

is_admin & admin_only:
    "Hey now, you're not an admin on this server!"

error_message:
    "OOPSIE WOOPSIE!! UwU We made a fucky wucky!! A wittle fucko boingo! The code "
    "monkeys at our headquarters are working VEWY HAWD to fix this!"

error_msg_forbidden:
    f"I can't DM you {msg.author.name}!"

"""

_TEST_SQLITE_FILE = "/testing_db.sqlite"


@pytest.fixture
def client(event_loop):
    from movienightbot.application import client, _server_controller
    from movienightbot.config import Config
    from movienightbot.db import initialize_db

    bconfig = Config("unused_token", f"sqlite://{_TEST_SQLITE_FILE}")
    bconfig.message_identifier = "m!"
    bconfig.port = 8000
    bconfig.base_url = f"http://localhost:{bconfig.port}/"

    client.loop = event_loop
    client.config = bconfig
    initialize_db(bconfig.db_url)

    test.configure(client)
    guild = client.guilds[0]
    guild_data = {"id": guild.id, "channel": guild.text_channels[0].id}
    _server_controller.create(guild_data)

    return client


async def _set_test_role(client, perms=discord.Permissions.all(), midx=0, gidx=0):
    guild = client.guilds[gidx]
    test_role = await guild.create_role(name="TestingRole", permissions=perms)
    await guild.members[midx].add_roles(test_role)
    return test_role


async def _clear_test_role(client, role, midx=0, gidx=0):
    guild = client.guilds[gidx]
    await guild.members[midx].remove_roles(role)
    await role.delete()


@pytest.mark.asyncio
async def test_cmd_unknown(client):
    await test.message("m!cmd_unknown")
    test.verify_message(
        "Unknown command cmd_unknown given, try reading the tutorial at `m!help` "
        "to see what commands are available!"
    )


@pytest.mark.asyncio
async def test_cmd_block_suggestions(client):
    # test admin command blocked first
    await test.message("m!block_suggestions on")
    test.verify_message("Hey now, you're not an admin on this server!")

    test_role = await _set_test_role(client)

    await test.message("m!block_suggestions")
    test.verify_message("Unknown option for block_suggestions: ", contains=True)

    await test.message("m!block_suggestions on")
    test.verify_message("Server suggestions are now disallowed")

    await test.message("m!block_suggestions off")
    test.verify_message("Server suggestions are now allowed")

    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_cancel_vote(client):
    pass


@pytest.mark.asyncio
async def test_cmd_check_movie_names(client):
    pass


@pytest.mark.asyncio
async def test_cmd_cleanup(client):
    pass


@pytest.mark.asyncio
async def test_cmd_end_vote(client):
    pass


@pytest.mark.asyncio
async def test_cmd_help(client):
    pass


@pytest.mark.asyncio
async def test_cmd_movie_option_count(client):
    pass


@pytest.mark.asyncio
async def test_cmd_remove(client):
    pass


@pytest.mark.asyncio
async def test_cmd_server_settings(client):
    pass


@pytest.mark.asyncio
async def test_cmd_set_admin_role(client):
    pass


@pytest.mark.asyncio
async def test_cmd_set_imdb_id(client):
    pass


@pytest.mark.asyncio
async def test_cmd_set_message_timeout(client):
    pass


@pytest.mark.asyncio
async def test_cmd_set_movie_channel(client):
    pass


@pytest.mark.asyncio
async def test_cmd_set_movie_time(client):
    pass


@pytest.mark.asyncio
async def test_cmd_set_watched(client):
    pass


@pytest.mark.asyncio
async def test_cmd_start_vote(client):
    pass


@pytest.mark.asyncio
async def test_cmd_suggest(client):
    """
    - "Could not find the movie title you suggested in IMDb."
    """

    test_title = "The Land Before Time"
    await test.message(f"m!suggest {test_title}")
    test.verify_message(
        f"Your suggestion of {test_title} () has been added to the list."
    )

    await test.message(f"m!suggest {test_title}")
    test.verify_message(f"{test_title} has already been suggested in this server.")

    test_role = await _set_test_role(client)
    await test.message("m!block_suggestions on")
    test.get_message()

    await _clear_test_role(client, test_role)
    await test.message(f"m!suggest {test_title}")
    test.verify_message("Suggestions are currently disabled on the server")

    test_role = await _set_test_role(client)
    await test.message("m!block_suggestions off")
    test.get_message()

    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_suggested(client):
    pass


@pytest.mark.asyncio
async def test_cmd_tie_option(client):
    pass


@pytest.mark.asyncio
async def test_cmd_unwatch(client):
    test_title = "The Land Before Time"
    await test.message(f"m!unwatch {test_title}")
    test.verify_message("Hey now, you're not an admin on this server!")

    test_role = await _set_test_role(client)

    await test.message(f"m!unwatch {test_title}")
    test.verify_message(f"No movie titled {test_title} has been watched")

    await test.message(f"m!suggest {test_title}")
    test.get_message()

    await test.message(f"m!unwatch {test_title}")
    test.verify_message(
        f"{test_title} has been set as unwatched and will show up in future votes."
    )

    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_user_vote_count(client):
    pass


@pytest.mark.asyncio
async def test_cmd_watched(client):
    pass
