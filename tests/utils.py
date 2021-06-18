import discord
import discord.ext.test as test


async def _set_test_role(client, perms=discord.Permissions.all(), midx=0, gidx=0):
    guild = client.guilds[gidx]
    test_role = await guild.create_role(name="TestingRole", permissions=perms)
    await guild.members[midx].add_roles(test_role)
    return test_role


async def _clear_test_role(client, role, midx=0, gidx=0):
    guild = client.guilds[gidx]
    await guild.members[midx].remove_roles(role)
    await role.delete()


async def _do_admin_test(test_msg, peek=False):
    m = await test.message(test_msg)
    t = test.verify().message().content("Hey now, you're not an admin on this server!")
    if peek:
        t.peek()
    assert t
    return m


async def _verify_deleted_message(client, msg_id, channel=0, guild=0):
    ch = client.guilds[guild].channels[channel]
    try:
        await ch.fetch_message(msg_id)
    except discord.NotFound:
        return True
    return False
