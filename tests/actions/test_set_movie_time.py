import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_set_movie_time(client):
    await test.empty_queue()
    time_str = "12:00"

    await _do_admin_test(f"m!set_movie_time {time_str}")

    test_role = await _set_test_role(client)
    await test.message(f"m!set_movie_time {time_str}PM")
    assert test.verify().message().content("Movie time given in invalid format. Must be `HH:MM`")

    await test.message(f"m!set_movie_time {time_str}")
    assert test.verify().message().content(f"Movie time updated to {time_str} UTC")
    await _clear_test_role(client, test_role)
