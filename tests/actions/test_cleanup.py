import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
    _verify_deleted_message,
)


@pytest.mark.asyncio
async def test_cleanup(client):
    m0 = await _do_admin_test("m!cleanup", peek=True)
    r0 = test.get_message()

    test_role = await _set_test_role(client)
    m1 = await test.message("m!suggested")
    r1 = test.get_message()
    m2 = await test.message("m!watched")
    r2 = test.get_message()
    m3 = await test.message("m!cleanup")
    assert test.verify().message().nothing()

    msgs = [m0, r0, m1, r1, m2, r2, m3]
    for msg in msgs:
        status = await _verify_deleted_message(client, msg.id)
        assert status is True, "Expected message to be deleted, but message still exists."

    await _clear_test_role(client, test_role)
