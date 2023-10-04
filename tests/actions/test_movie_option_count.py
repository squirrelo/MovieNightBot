import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_movie_option_count(client):
    await test.empty_queue()
    test_number = 7

    await _do_admin_test(f"m!movie_option_count {test_number}")

    test_role = await _set_test_role(client)
    await test.message(f"m!movie_option_count {test_number}")
    assert test.verify().message().content(f"Number of movies per vote updated to {test_number}")

    tests = [0, 1, 26, 27]
    for test_number in tests:
        await test.message(f"m!movie_option_count {test_number}")
        assert (
            test.verify()
            .message()
            .content("Failed to update: Number of movies per vote must be between 2 and 25, inclusive")
        )
    await _clear_test_role(client, test_role)
