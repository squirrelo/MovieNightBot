import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)
from movienightbot.util import build_vote_embed


@pytest.mark.asyncio
async def test_start_vote(client):
    await test.empty_queue()

    await _do_admin_test("m!start_vote")

    test_role = await _set_test_role(client)
    await test.message("m!start_vote")
    test_embed = build_vote_embed(client.guilds[0].id)
    assert test.verify().message().embed(test_embed)

    # clean up the vote state.
    await test.message("m!end_vote")
    test.get_message()
    await _clear_test_role(client, test_role)
