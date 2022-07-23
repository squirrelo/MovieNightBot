import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _set_test_role,
)
from movienightbot.util import build_vote_embed, emojis_text


@pytest.mark.asyncio
async def test_end_vote_tiebreaker(client):
    await test.empty_queue()
    cfg = test.get_config()
    tester1 = cfg.members[0]
    tester2 = cfg.members[1]

    await test.message("m!end_vote")
    assert test.verify().message().content("No vote started!")

    # So you CAN start a vote without any or enough suggested titles.
    # TODO: Fix that...

    await test.message("m!suggest The Shining")
    test.get_message()
    await test.message("m!suggest Pulp Fiction")
    test.get_message()
    await test.message("m!suggest Bad Santa")
    test.get_message()
    await test.message("m!suggest Hook")
    test.get_message()
    await test.message("m!suggest The Little Mermaid")
    test.get_message()
    await test.message("m!suggest A Nightmare on Elm Street")
    test.get_message()
    await test.message("m!suggest Final Fantasy: The Spirits Within")
    test.get_message()

    test_role = await _set_test_role(client)
    m = await test.message("m!start_vote")
    test_embed = build_vote_embed(m.channel.guild.id)
    vote_msg = test.get_message(peek=True)
    assert test.verify().message().embed(test_embed).peek()
    await _clear_test_role(client, test_role)

    await test.add_reaction(
        message=vote_msg, user=tester1, emoji=emojis_text[":regional_indicator_a:"]
    )
    await test.add_reaction(
        message=vote_msg, user=tester2, emoji=emojis_text[":regional_indicator_b:"]
    )

    await test.message("m!end_vote")
    tie_vote_embed = build_vote_embed(m.channel.guild.id)
    assert (
        tie_vote_embed is not vote_msg.embeds[0]
    ), "Vote embed was not updated with tie breaker embed."

    await test.add_reaction(
        message=vote_msg, user=tester1, emoji=emojis_text[":regional_indicator_a:"]
    )
    await test.add_reaction(
        message=vote_msg, user=tester2, emoji=emojis_text[":regional_indicator_a:"]
    )

    test.get_message()
    assert (
        test.verify()
        .message()
        .content("There was a tie! Check the vote message for new vote options")
    )

    await test.message("m!end_vote")
    assert test.verify().message().contains().content("The winning vote was `")


@pytest.mark.asyncio
async def test_end_vote_winner(client):
    cfg = test.get_config()
    tester1 = cfg.members[0]
    tester2 = cfg.members[1]

    await test.message("m!end_vote")
    assert test.verify().message().content("No vote started!")

    # So you CAN start a vote without any or enough suggested titles.
    # TODO: Fix that...

    await test.message("m!suggest The Shining")
    test.get_message()
    await test.message("m!suggest Pulp Fiction")
    test.get_message()
    await test.message("m!suggest Bad Santa")
    test.get_message()
    await test.message("m!suggest Hook")
    test.get_message()
    await test.message("m!suggest The Little Mermaid")
    test.get_message()
    await test.message("m!suggest A Nightmare on Elm Street")
    test.get_message()
    await test.message("m!suggest Final Fantasy: The Spirits Within")
    test.get_message()

    test_role = await _set_test_role(client)
    m = await test.message("m!start_vote")
    test_embed = build_vote_embed(m.channel.guild.id)

    assert test.verify().message().embed(test_embed).peek()
    vote_msg = test.get_message(peek=True)
    await _clear_test_role(client, test_role)

    await test.add_reaction(
        user=tester1, message=vote_msg, emoji=emojis_text[":regional_indicator_a:"]
    )
    await test.add_reaction(
        user=tester2, message=vote_msg, emoji=emojis_text[":regional_indicator_a:"]
    )
    test.get_message()

    await test.message("m!end_vote")
    assert test.verify().message().contains().content("The winning vote was `")
