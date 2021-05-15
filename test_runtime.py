import discord
import discord.ext.test as test
import pytest


from movienightbot.actions.help import HelpAction
from movienightbot.actions.server_settings import ServerSettingsAction
from movienightbot.application import client as BotClient, _server_controller
from movienightbot.config import Config
from movienightbot.db import initialize_db
from movienightbot.util import build_vote_embed


"""


guild_only:
    "You can't do this command from a DM!"

error_message:
    "OOPSIE WOOPSIE!! UwU We made a fucky wucky!! A wittle fucko boingo! The code "
    "monkeys at our headquarters are working VEWY HAWD to fix this!"

error_msg_forbidden:
    f"I can't DM you {msg.author.name}!"

"""

_TEST_SQLITE_FILE = "/testing_db.sqlite"


@pytest.fixture
def client(event_loop):

    bconfig = Config("unused_token", f"sqlite://{_TEST_SQLITE_FILE}")
    bconfig.message_identifier = "m!"
    bconfig.port = 8000
    bconfig.base_url = f"http://localhost:{bconfig.port}"

    bclient = BotClient
    bclient.loop = event_loop
    bclient.config = bconfig
    initialize_db(bconfig.db_url)

    test.configure(bclient)
    guild = bclient.guilds[0]
    guild_data = {"id": guild.id, "channel": guild.text_channels[0].id}
    _server_controller.create(guild_data)

    return bclient


async def _set_test_role(client, perms=discord.Permissions.all(), midx=0, gidx=0):
    guild = client.guilds[gidx]
    test_role = await guild.create_role(name="TestingRole", permissions=perms)
    await guild.members[midx].add_roles(test_role)
    return test_role


async def _clear_test_role(client, role, midx=0, gidx=0):
    guild = client.guilds[gidx]
    await guild.members[midx].remove_roles(role)
    await role.delete()


async def _do_admin_test(test_msg, peek=False):
    m = await test.message(test_msg)
    test.verify_message("Hey now, you're not an admin on this server!", peek=peek)
    return m


async def _verify_deleted_message(client, msg_id, channel=0, guild=0):
    ch = client.guilds[guild].channels[channel]
    try:
        await ch.fetch_message(msg_id)
    except discord.NotFound:
        return True
    return False


@pytest.mark.asyncio
async def test_cmd_unknown(client):
    await test.empty_queue()

    await test.message("m!cmd_unknown")
    test.verify_message(
        "Unknown command cmd_unknown given, try reading the tutorial at `m!help` "
        "to see what commands are available!"
    )


@pytest.mark.asyncio
async def test_cmd_block_suggestions(client):
    await test.empty_queue()

    # test admin command blocked first
    await _do_admin_test("m!block_suggestions on")

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
    await test.empty_queue()

    await _do_admin_test("m!check_movie_names on")

    test_role = await _set_test_role(client)
    await test.message("m!check_movie_names x")
    test.verify_message("Unknown option for check_movie_names: `x`")

    await test.message("m!check_movie_names on")
    test.verify_message("IMDB movie name checks are now on")

    await test.message("m!check_movie_names off")
    test.verify_message("IMDB movie name checks are now off")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_cleanup(client):
    await test.empty_queue()

    m0 = await _do_admin_test("m!cleanup", peek=True)
    r0 = test.get_message()

    test_role = await _set_test_role(client)
    m1 = await test.message("m!suggested")
    r1 = test.get_message()
    m2 = await test.message("m!watched")
    r2 = test.get_message()
    m3 = await test.message("m!cleanup")
    test.verify_message(assert_nothing=True)

    msgs = [m0, r0, m1, r1, m2, r2, m3]
    for msg in msgs:
        status = await _verify_deleted_message(client, msg.id)
        assert (
            status is True
        ), "Expected message to be deleted, but message still exists."

    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_end_vote(client):
    pass


@pytest.mark.asyncio
async def test_cmd_help(client):
    await test.empty_queue()
    ha = HelpAction()
    test_embed = ha._build_help_embed(client.guilds[0].id)

    await test.message("m!help")
    test.verify_embed(embed=test_embed, allow_text=True)


@pytest.mark.asyncio
async def test_cmd_movie_option_count(client):
    await test.empty_queue()
    test_number = 7

    await _do_admin_test(f"m!movie_option_count {test_number}")

    test_role = await _set_test_role(client)
    await test.message(f"m!movie_option_count {test_number}")
    test.verify_message(f"Number of movies per vote updated to {test_number}")

    tests = [0, 1, 26, 27]
    for test_number in tests:
        await test.message(f"m!movie_option_count {test_number}")
        test.verify_message(
            "Failed to update: Number of movies per vote must be between 2 and 25, inclusive"
        )
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_remove(client):
    await test.empty_queue()
    test_title = "The Land Before Time"

    await _do_admin_test(f"m!remove {test_title}")

    test_role = await _set_test_role(client)
    await test.message(f"m!remove {test_title}")
    test.verify_message(f"Movie {test_title} has not been suggested")

    await test.message(f"m!suggest {test_title}")
    test.get_message()
    await test.message(f"m!remove {test_title}")
    test.verify_message(f"The movie {test_title} has been removed from the list.")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_server_settings(client):
    await test.empty_queue()
    ssa = ServerSettingsAction()
    test_embed = ssa.format_embed(client.guilds[0].id)

    await _do_admin_test("m!server_settings")

    test_role = await _set_test_role(client)
    await test.message("m!server_settings")
    test.verify_embed(embed=test_embed, allow_text=True)
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_set_admin_role(client):
    await test.empty_queue()
    role_name = "AdminRole"

    await _do_admin_test(f"m!set_admin_role {role_name}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_admin_role {role_name}")
    test.verify_message(f"Role not found: {role_name}.")

    await test.message(f"m!set_admin_role {test_role.name}")
    test.verify_message(f"Admin role updated to {test_role.name}")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_set_imdb_id(client):
    await test.empty_queue()

    # The Land Before Time (1988)
    # https://www.imdb.com/title/tt0095489/
    test_title = "The Land Before Time"
    test_id = "0095489"
    await test.message(f"m!set_imdb_id {test_id} {test_title}")
    test.verify_message(f"Unable to update IMDB id for {test_title}")

    await test.message(f"m!suggest {test_title}")
    test.get_message()
    await test.message(f"m!set_imdb_id {test_id} {test_title}")
    test.verify_message(f"Movie {test_title} has been updated to imdb ID {test_id}")

    # not sure how to reach this output...
    # test_title2 = test_title[:-4]
    # await test.message(f"m!suggest {test_title2}")
    # test.get_message()
    # await test.message(f"m!set_imdb_id {test_id} {test_title2}")
    # test.verify_message(f"Movie {test_title2} updated multiple entries to IMDB id {test_id}")
    return


@pytest.mark.asyncio
async def test_cmd_set_message_timeout(client):
    await test.empty_queue()
    timeout = 10

    await _do_admin_test(f"m!set_message_timeout {timeout}")

    timeout = "TT"
    test_role = await _set_test_role(client)
    await test.message(f"m!set_message_timeout {timeout}")
    test.verify_message(f"Must send an number, got {timeout}")

    timeout = -2
    await test.message(f"m!set_message_timeout {timeout}")
    test.verify_message(f"Timeout value must be >= 0, got {timeout}")

    timeout = 10
    await test.message(f"m!set_message_timeout {timeout}")
    test.verify_message(f"Message timeout updated to {timeout} seconds")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_set_movie_channel(client):
    await test.empty_queue()
    channel = "TestChannel"

    await _do_admin_test(f"m!set_channel {channel}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_channel {channel}")
    test.verify_message(f"Failed update: unknown channel {channel} given.")

    channel = client.guilds[0].channels[0].name
    await test.message(f"m!set_channel {channel}")
    test.verify_message(f"Bot channel updated to {channel}")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_set_movie_time(client):
    await test.empty_queue()
    time_str = "12:00"

    await _do_admin_test(f"m!set_movie_time {time_str}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_movie_time {time_str}PM")
    test.verify_message("Movie time given in invalid format. Must be `HH:MM`")

    await test.message(f"m!set_movie_time {time_str}")
    test.verify_message(f"Movie time updated to {time_str} UTC")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_set_watched(client):
    await test.empty_queue()
    watched = "Some Movie Title"

    await _do_admin_test(f"m!set_watched {watched}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_watched {watched}")
    test.verify_message(f"No movie titled {watched} has been suggested")

    await test.message(f"m!suggest {watched}")
    test.get_message()
    await test.message(f"m!set_watched {watched}")
    test.verify_message(
        f"{watched} has been set as watched and will no longer show up in future votes."
    )
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_start_vote(client):
    await test.empty_queue()

    await _do_admin_test("m!start_vote")

    test_role = await _set_test_role(client)
    await test.message("m!start_vote")
    test_embed = build_vote_embed(client.guilds[0].id)
    test.verify_embed(embed=test_embed, allow_text=True)

    # clean up the vote state.
    await test.message("m!end_vote")
    test.get_message()
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_suggest(client):
    """
    - "Could not find the movie title you suggested in IMDb."
    """
    await test.empty_queue()

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
    await test.empty_queue()

    base_url = client.config.base_url
    guild_id = client.guilds[0].id
    await test.message("m!suggested")
    test.verify_message(f"Suggestions can be found at {base_url}/suggested/{guild_id}")


@pytest.mark.asyncio
async def test_cmd_tie_option(client):
    await test.empty_queue()

    await _do_admin_test("m!tie_option random")

    test_role = await _set_test_role(client)
    await test.message("m!tie_option silly-non-option")
    test.verify_message("Unknown tiebreaker option given: silly-non-option")

    await test.message("m!tie_option random")
    test.verify_message("Tiebreaker updated to random")

    await test.message("m!tie_option breaker")
    test.verify_message("Tiebreaker updated to breaker")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_unwatch(client):
    await test.empty_queue()

    test_title = "The Land Before Time"
    await _do_admin_test(f"m!unwatch {test_title}")

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
    # Writing this test I realized that the setting is a one-way setting.
    # Once you go higher, you cannot go lower again. Should this be?
    await test.empty_queue()

    await _do_admin_test("m!user_vote_count 0")

    test_role = await _set_test_role(client)
    await test.message("m!user_vote_count 0")
    test.verify_message("Failed to update: Number of votes per user must be > 0")

    await test.message("m!user_vote_count 1")
    test.verify_message("Failed to update: Number of votes per user must be >= 4")

    await test.message("m!user_vote_count 6")
    test.verify_message("Number of votes per user updated to 6")
    await _clear_test_role(client, test_role)


@pytest.mark.asyncio
async def test_cmd_watched(client):
    await test.empty_queue()

    base_url = client.config.base_url
    guild_id = client.guilds[0].id
    await test.message("m!watched")
    test.verify_message(f"Watched movies can be found at {base_url}/watched/{guild_id}")
