import asyncio
import datetime
import logging
import re
from typing import Optional, Union

import discord
import imdbinfo
import peewee as pw

from .db.controllers import MovieVote, MovieVoteController, ServerController
from .exc import VoteError

logger = logging.getLogger("movienightbot")


def is_admin(interaction: discord.Interaction) -> bool:
    if interaction.user.id == interaction.guild.owner_id:
        logging.debug("User {} is guild owner", interaction.user.name)
        return True
    server_settings = ServerController().get_by_id(interaction.guild.id)
    for role in interaction.user.roles:
        if server_settings.admin_role == role.name:
            logging.debug("User {} is in role {}.", interaction.user.name, server_settings.admin_role)
            return True

    logging.debug(
        "User {} is not part of role {}. User has roles {}",
        interaction.user.name,
        server_settings.admin_role,
        str([r.name for r in interaction.user.roles]),
    )
    return False


async def get_message(channel: discord.TextChannel, msg_id: int) -> Union[None, discord.Message]:
    """Retrives a message, or returns None if cannot retrieve the message"""
    try:
        return await channel.fetch_message(msg_id)
    except (
        discord.errors.NotFound,
        discord.errors.HTTPException,
        discord.errors.Forbidden,
    ):
        return None


async def delete_thread(thread: discord.Thread, sec_delay: int = 10) -> None:
    """Deletes a list of messages off a server

    Parameters
    ----------
    thread : List of doscord.Message objects
        The messages to delete
    sec_delay : int
        The number of seconds to wait before deleting the message. Default 10

    """
    if sec_delay <= 0:
        # want messages to stay indefinitely so do nothing
        return
    await asyncio.sleep(sec_delay)
    await thread.delete()


def build_vote_embed(server_id: int):
    from movienightbot.application import bot

    server_row = ServerController().get_by_id(server_id)
    try:
        movie_rows = MovieVoteController().get_movies_for_server_vote(server_id)
    except pw.DoesNotExist:
        raise VoteError(f"No vote started for server {server_id}")  # noqa: B904
    embed = discord.Embed(
        title="Movie Vote!",
        description=f"""Use the emojis to vote on your preferred movies, in the order you would prefer them.
You may vote for up to {server_row.num_votes_per_user} movies.
Reset your votes with the :arrows_counterclockwise: emoji.""",
    )
    for movie_vote in movie_rows:
        movie = movie_vote.movie
        imdb_info = movie.imdb_id
        movie_info = f"{movie_vote.emoji} {movie.movie_name}"
        score = f"Score: {movie_vote.score:.2f}"
        if imdb_info:
            movie_info += f" ({imdb_info.year})"
            score += f" - [IMDb Page](https://www.imdb.com/title/tt{imdb_info.imdb_id}/)"

        embed.add_field(
            name=movie_info,
            value=score,
            inline=False,
        )

    embed.add_field(
        name="View more details here:",
        value=f"{bot.config.base_url}/vote.html?server={server_id}",
        inline=False,
    )
    embed.set_footer(text="Movie time is")
    today = datetime.datetime.utcnow().date()
    movie_hour, movie_minute = server_row.movie_time.split(":")
    movie_time = datetime.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
        hour=int(movie_hour),
        minute=int(movie_minute),
        tzinfo=datetime.timezone.utc,
    )
    embed.timestamp = movie_time
    return embed


emojis_text = {
    ":regional_indicator_a:": "🇦",
    ":regional_indicator_b:": "🇧",
    ":regional_indicator_c:": "🇨",
    ":regional_indicator_d:": "🇩",
    ":regional_indicator_e:": "🇪",
    ":regional_indicator_f:": "🇫",
    ":regional_indicator_g:": "🇬",
    ":regional_indicator_h:": "🇭",
    ":regional_indicator_i:": "🇮",
    ":regional_indicator_j:": "🇯",
    ":regional_indicator_k:": "🇰",
    ":regional_indicator_l:": "🇱",
    ":regional_indicator_m:": "🇲",
    ":regional_indicator_n:": "🇳",
    ":regional_indicator_o:": "🇴",
    ":regional_indicator_p:": "🇵",
    ":regional_indicator_q:": "🇶",
    ":regional_indicator_r:": "🇷",
    ":regional_indicator_s:": "🇸",
    ":regional_indicator_t:": "🇹",
    ":regional_indicator_u:": "🇺",
    ":regional_indicator_v:": "🇻",
    ":regional_indicator_w:": "🇼",
    ":regional_indicator_x:": "🇽",
    ":regional_indicator_y:": "🇾",
    ":regional_indicator_z:": "🇿",
    ":octagonal_sign:": "🛑",
    ":arrows_counterclockwise:": "🔄",
}


emojis_unicode = {v: k for k, v in emojis_text.items()}


imdb_url_regex = re.compile(r"title/tt([0-9]+)")


async def add_vote_emojis(vote_msg: discord.Message, movie_votes: MovieVote):
    for movie_vote in movie_votes:
        await vote_msg.add_reaction(emojis_text[movie_vote.emoji])
    await vote_msg.add_reaction(emojis_text[":arrows_counterclockwise:"])

def get_imdb_info_by_id(imdb_id: Union[int, str]) -> Union[None, imdbinfo.services.MovieDetail]:
    if not imdb_id:
        return None

    return imdbinfo.get_movie(str(imdb_id))


def get_imdb_info(movie_name: str, kind: Optional[str] = None, year: Optional[int] = None) -> Union[None, imdbinfo.services.MovieDetail]:
    if not movie_name:
        return None

    if movie_name.lower().startswith("http"):
        movie_id = imdb_url_regex.findall(movie_name)
        logger.debug("movie regex: `{}` >> {}", movie_name, movie_id)
        if len(movie_id) == 1:
            imdb_id = movie_id[0]
            return_movie = get_imdb_info_by_id(imdb_id)
        else:
            return None
    else:
        logger.debug(f"searching for `{movie_name}`")
        results = imdbinfo.search_title(movie_name)
        logger.debug("IMDB RESULTS: {}", str(results))
        for r in results.titles:
            if kind and kind != r.kind:
                continue
            if year and year != r.year:
                continue
            if r.title.lower() == movie_name.lower():
                logger.debug("{} Matched {}", movie_name, r)
                return_movie = r
                break
        # for/else hell yeah!
        else:
            logger.debug("{} Unmatched", movie_name)
            return None

    return return_movie


def capitalize_movie_name(movie_name: str) -> str:
    clean_name = []
    for word in movie_name.strip().split(" "):
        if not word:
            continue
        clean_name.append(word.capitalize())
    return " ".join(clean_name)


DEFAULT_PERMISSIONS = discord.Permissions(403727019072)


async def generate_invite_link(permissions=DEFAULT_PERMISSIONS, guild=None):
    from movienightbot.application import bot

    app_info = await bot.application_info()
    args = dict(client_id=app_info.id, permissions=permissions)
    # Need to do it this way so we don't send guild property at all if it's None. Yay discord.py limitations.
    if guild is not None:
        args["guild"] = guild
    return discord.utils.oauth_url(**args)
