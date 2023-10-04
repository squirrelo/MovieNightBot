import pytest
import discord.ext.test as test


@pytest.mark.asyncio
async def test_watched(client):
    await test.empty_queue()

    base_url = client.config.base_url
    guild_id = client.guilds[0].id
    await test.message("m!watched")
    assert (
        test.verify()
        .message()
        .content(f"Watched movies can be found at {base_url}/movies.html?server={guild_id}&view=watched")
    )
