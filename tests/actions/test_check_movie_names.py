import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_check_movie_names(client):
    await test.empty_queue()

    await _do_admin_test("m!check_movie_names on")

    test_role = await _set_test_role(client)
    await test.message("m!check_movie_names x")
    assert test.verify().message().content("Unknown option for check_movie_names: `x`")

    await test.message("m!check_movie_names on")
    assert test.verify().message().content("IMDB movie name checks are now on")

    # TODO: add tests for when this option is enabled, since it changes returned data.

    await test.message("m!check_movie_names off")
    assert test.verify().message().content("IMDB movie name checks are now off")
    await _clear_test_role(client, test_role)
