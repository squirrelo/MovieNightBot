import pytest
import discord.ext.test as test


@pytest.mark.asyncio
async def test_unknown(client):
    await test.message("m!cmd_unknown")
    assert (
        test.verify()
        .message()
        .content(
            "Unknown command cmd_unknown given, try reading the tutorial at `m!help` "
            "to see what commands are available!"
        )
    )
