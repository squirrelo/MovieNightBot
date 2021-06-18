import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_set_watched(client):
    await test.empty_queue()
    watched = "Some Movie Title"

    await _do_admin_test(f"m!set_watched {watched}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_watched {watched}")
    assert (
        test.verify().message().content(f"No movie titled {watched} has been suggested")
    )

    await test.message(f"m!suggest {watched}")
    test.get_message()
    await test.message(f"m!set_watched {watched}")
    assert (
        test.verify()
        .message()
        .content(
            f"{watched} has been set as watched and will no longer show up in future votes."
        )
    )
    await _clear_test_role(client, test_role)
