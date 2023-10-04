import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_user_vote_count(client):
    # Writing this test I realized that the setting is a one-way setting.
    # Once you go higher, you cannot go lower again. Should this be?
    await test.empty_queue()

    await _do_admin_test("m!user_vote_count 0")

    test_role = await _set_test_role(client)
    await test.message("m!user_vote_count 0")
    assert test.verify().message().content("Failed to update: Number of votes per user must be > 0")

    await test.message("m!user_vote_count 1")
    assert test.verify().message().content("Failed to update: Number of votes per user must be >= 4")

    await test.message("m!user_vote_count 6")
    assert test.verify().message().content("Number of votes per user updated to 6")
    await _clear_test_role(client, test_role)
