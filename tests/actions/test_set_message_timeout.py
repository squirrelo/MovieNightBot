import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_set_message_timeout(client):
    await test.empty_queue()
    timeout = 10

    await _do_admin_test(f"m!set_message_timeout {timeout}")

    timeout = "TT"
    test_role = await _set_test_role(client)
    await test.message(f"m!set_message_timeout {timeout}")
    assert test.verify().message().content(f"Must send an number, got {timeout}")

    timeout = -2
    await test.message(f"m!set_message_timeout {timeout}")
    assert test.verify().message().content(f"Timeout value must be >= 0, got {timeout}")

    timeout = 10
    await test.message(f"m!set_message_timeout {timeout}")
    assert (
        test.verify().message().content(f"Message timeout updated to {timeout} seconds")
    )
    await _clear_test_role(client, test_role)
