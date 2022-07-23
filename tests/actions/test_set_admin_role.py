import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_set_admin_role(client):
    await test.empty_queue()
    role_name = "AdminRole"

    await _do_admin_test(f"m!set_admin_role {role_name}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_admin_role {role_name}")
    assert test.verify().message().content(f"Role not found: {role_name}.")

    await test.message(f"m!set_admin_role {test_role.name}")
    assert test.verify().message().content(f"Admin role updated to {test_role.name}")
    await _clear_test_role(client, test_role)
