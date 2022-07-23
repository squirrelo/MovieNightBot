import pytest
import discord.ext.test as test


@pytest.mark.asyncio
async def test_set_imdb_id(client):
    await test.empty_queue()

    # The Land Before Time (1988)
    # https://www.imdb.com/title/tt0095489/
    test_title = "The Land Before Time"
    test_id = "0095489"
    await test.message(f"m!set_imdb_id {test_id} {test_title}")
    assert test.verify().message().content(f"Unable to update IMDB id for {test_title}")

    await test.message(f"m!suggest {test_title}")
    test.get_message()
    await test.message(f"m!set_imdb_id {test_id} {test_title}")
    assert (
        test.verify()
        .message()
        .content(f"Movie {test_title} has been updated to imdb ID {test_id}")
    )

    # not sure how to reach this output...
    # test_title2 = test_title[:-4]
    # await test.message(f"m!suggest {test_title2}")
    # test.get_message()
    # await test.message(f"m!set_imdb_id {test_id} {test_title2}")
    # assert test.verify().message().content(f"Movie {test_title2} updated multiple entries to IMDB id {test_id}")
