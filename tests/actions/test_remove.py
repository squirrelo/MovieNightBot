import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_remove(client):
    await test.empty_queue()
    test_title = "The Land Before Time"

    await _do_admin_test(f"m!remove {test_title}")

    test_role = await _set_test_role(client)
    await test.message(f"m!remove {test_title}")
    assert test.verify().message().content(f"Movie {test_title} has not been suggested")

    await test.message(f"m!suggest {test_title}")
    test.get_message()
    await test.message(f"m!remove {test_title}")
    assert test.verify().message().content(f"The movie {test_title} has been removed from the list.")
    await _clear_test_role(client, test_role)
