import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_tie_option(client):
    await test.empty_queue()

    await _do_admin_test("m!tie_option random")

    test_role = await _set_test_role(client)
    await test.message("m!tie_option silly-non-option")
    assert (
        test.verify()
        .message()
        .content("Unknown tiebreaker option given: silly-non-option")
    )

    await test.message("m!tie_option random")
    assert test.verify().message().content("Tiebreaker updated to random")

    await test.message("m!tie_option breaker")
    assert test.verify().message().content("Tiebreaker updated to breaker")
    await _clear_test_role(client, test_role)
