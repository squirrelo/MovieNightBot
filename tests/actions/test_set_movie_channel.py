import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_set_movie_channel(client):
    await test.empty_queue()
    channel = "DummyTestChannel"

    await _do_admin_test(f"m!set_channel {channel}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_channel {channel}")
    assert test.verify().message().content(f"Failed update: unknown channel {channel} given.")

    channel = client.guilds[0].channels[0].name
    await test.message(f"m!set_channel {channel}")
    assert test.verify().message().content(f"Bot channel updated to {channel}")
    await _clear_test_role(client, test_role)
