import pytest
import discord.ext.test as test


@pytest.mark.asyncio
async def test_suggested(client):
    await test.empty_queue()

    base_url = client.config.base_url
    guild_id = client.guilds[0].id
    await test.message("m!suggested")
    assert (
        test.verify()
        .message()
        .content(f"Suggestions can be found at {base_url}/suggested/{guild_id}")
    )
