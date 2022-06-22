import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_unwatch(client):
    await test.empty_queue()

    test_title = "The Land Before Time"
    await _do_admin_test(f"m!unwatch {test_title}")

    test_role = await _set_test_role(client)
    await test.message(f"m!unwatch {test_title}")
    assert (
        test.verify()
        .message()
        .content(f"No movie titled {test_title} has been watched")
    )

    await test.message(f"m!suggest {test_title}")
    test.get_message()

    await test.message(f"m!unwatch {test_title}")
    assert (
        test.verify()
        .message()
        .content(
            f"{test_title} has been set as unwatched and will show up in future votes."
        )
    )
    await _clear_test_role(client, test_role)
