import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_block_suggestions(client):
    # test admin command blocked first
    await _do_admin_test("m!block_suggestions on")

    test_role = await _set_test_role(client)

    await test.message("m!block_suggestions")
    assert test.verify().message().content("Unknown option for block_suggestions: ``")

    await test.message("m!block_suggestions on")
    assert test.verify().message().content("Server suggestions are now disallowed")

    await test.message("m!block_suggestions off")
    assert test.verify().message().content("Server suggestions are now allowed")

    await _clear_test_role(client, test_role)
