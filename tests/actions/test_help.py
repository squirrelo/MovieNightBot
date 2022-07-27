import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _set_test_role,
)
from movienightbot.actions.help import HelpAction


@pytest.mark.asyncio
async def test_help(client):
    await test.empty_queue()
    ha = HelpAction()
    test_embed = ha._build_help_embed_general(False)
    test_admin_embed = ha._build_help_embed_general(True)

    await test.message("m!help")
    assert test.verify().message().embed(test_embed)

    test_role = await _set_test_role(client)
    await test.message("m!set_admin_role TestingRole")
    test.get_message()

    await test.message("m!help")
    assert test.verify().message().embed(test_admin_embed)
    await _clear_test_role(client, test_role)
