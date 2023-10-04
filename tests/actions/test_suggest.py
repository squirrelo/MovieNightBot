import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_suggest(client):
    """
    - "Could not find the movie title you suggested in IMDb."
    """
    await test.empty_queue()

    test_title = "The Land Before Time"
    await test.message(f"m!suggest {test_title}")
    assert test.verify().message().content(f"Your suggestion of {test_title} () has been added to the list.")

    await test.message(f"m!suggest {test_title}")
    assert test.verify().message().content(f"{test_title} has already been suggested in this server.")


@pytest.mark.asyncio
async def test_suggest_blocked(client):
    await test.empty_queue()

    test_title = "The Land Before Time"
    test_role = await _set_test_role(client)
    await test.message("m!block_suggestions on")
    test.get_message()

    await _clear_test_role(client, test_role)
    await test.message(f"m!suggest {test_title}")
    assert test.verify().message().content("Suggestions are currently disabled on the server")

    test_role = await _set_test_role(client)
    await test.message("m!block_suggestions off")
    test.get_message()
    await _clear_test_role(client, test_role)
