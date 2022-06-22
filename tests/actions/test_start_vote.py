import pytest
import discord.ext.test as test


from tests.utils import (
    _do_admin_test,
    _add_movies,
    _set_test_role,
)
from movienightbot.util import build_vote_embed


@pytest.mark.asyncio
async def test_start_vote(client):
    await test.empty_queue()

    await _add_movies(client, ["TestMovie1", "TestMovie2", "TestMovie3"])

    await _set_test_role(client)
    await test.message("m!start_vote")
    test_embed = build_vote_embed(client.guilds[0].id)
    assert test.verify().message().embed(test_embed)


@pytest.mark.asyncio
async def test_start_vote_not_admin(client):
    await test.empty_queue()

    await test.message("m!start_vote")
    assert test.get_message().content == "Hey now, you're not an admin on this server!"


@pytest.mark.asyncio
async def test_start_vote_no_movies(client):
    await test.empty_queue()

    await _do_admin_test("m!start_vote")

    await _set_test_role(client)
    await test.message("m!start_vote")
    assert test.verify().message().content("No movies found")
