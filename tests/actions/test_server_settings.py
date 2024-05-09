import discord.ext.test as test
import pytest

from movienightbot.commands.server_setup_commands import ServerAdmin
from tests.utils import (
    _clear_test_role,
    _do_admin_test,
    _set_test_role,
)


@pytest.mark.asyncio
async def test_server_settings(client):
    await test.empty_queue()
    ssa = ServerAdmin()
    test_embed = ssa._format_server_embed(client.guilds[0].id)

    await _do_admin_test("m!server_settings")

    test_role = await _set_test_role(client)
    await test.message("m!server_settings")
    assert test.verify().message().embed(test_embed)
    await _clear_test_role(client, test_role)
