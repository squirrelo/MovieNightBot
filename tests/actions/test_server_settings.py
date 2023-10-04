import pytest
import discord.ext.test as test


from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)
from movienightbot.commands.server_settings import ServerSettingsAction


@pytest.mark.asyncio
async def test_server_settings(client):
    await test.empty_queue()
    ssa = ServerSettingsAction()
    test_embed = ssa.format_embed(client.guilds[0].id)

    await _do_admin_test("m!server_settings")

    test_role = await _set_test_role(client)
    await test.message("m!server_settings")
    assert test.verify().message().embed(test_embed)
    await _clear_test_role(client, test_role)
