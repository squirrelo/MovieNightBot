import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_cancel_vote(client):
    await test.message("m!cancel_vote")
    assert test.verify().message().content("No vote started!")

    test_role = await _set_test_role(client)
    await test.message("m!start_vote")
    test.get_message()
    await _clear_test_role(client, test_role)
    await test.message("m!cancel_vote")

    # TODO: figure out why I cannot verify the edited embed...
    #  It simply doesn't edit.
    #  Using peek=True to leave it on the stack doesn't help, unlike end_vote_tie.

    assert test.verify().message().content("Vote cancelled")
