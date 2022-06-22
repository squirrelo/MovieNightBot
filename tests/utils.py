from typing import List, Dict, Any, Optional

import discord
import discord.ext.test as test

from movienightbot.db.models import MovieGenre, Movie, IMDBInfo


async def _set_test_role(client, perms=discord.Permissions.all(), midx=0, gidx=0):
    guild = client.guilds[gidx]
    test_role = await guild.create_role(name="TestingRole", permissions=perms)
    await guild.members[midx].add_roles(test_role)
    return test_role


async def _clear_test_role(client, role, midx=0, gidx=0):
    guild = client.guilds[gidx]
    await guild.members[midx].remove_roles(role)
    await role.delete()


async def _add_movies(
    client,
    movie_names: List[str],
    imdb_info: Optional[List[Dict[str, Any]]] = None,
    gidx: int = 0,
):
    guild_id = client.guilds[gidx].id
    if imdb_info is not None:
        if len(movie_names) != len(imdb_info):
            raise ValueError("Mismatched lengths for movie_names and imdb_info")
        imdb_ids = [IMDBInfo.create(**c).id for c in imdb_info]
    else:
        imdb_ids = [None for x in range(len(movie_names))]
    movies = []
    for movie_name, imdb_id in zip(movie_names, imdb_ids):
        movie_info = {
            "imdb_id": imdb_id,
            "movie_name": movie_name,
            "server": guild_id,
            "suggested_by": "test_user",
        }
        movies.append(Movie.create(**movie_info))


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
