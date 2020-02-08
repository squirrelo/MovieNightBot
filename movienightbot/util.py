import discord

from .db.controllers import ServerController, MovieVoteController


def build_vote_embed(server_id: int):
    server_row = ServerController().get_by_id(server_id)
    movie_rows = MovieVoteController().get_movies_for_server_vote(server_id)
    embed = discord.Embed(
        title="Movie Vote!",
        description="Use the emojis to vote on your preferred movies, in the order you would prefer them. "
        f"You may vote for up to {server_row.num_votes_per_user} movies. "
        "If you need to reset your votes, use the :arrows_counterclockwise: emoji. "
        "To stop the vote, use the :stop_sign: emoji.",
    )
    for movie_vote in movie_rows:
        embed.add_field(
            name=f"{movie_vote.emoji} {movie_vote.movie.movie_name}",
            value=f"Score: {movie_vote.score}",
            inline=False,
        )
    embed.set_footer(text=f"Movie time is {server_row.movie_time} UTC")
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
    ":stop_sign:": "🛑",
    ":arrows_counterclockwise:": "🔄",
}


emojis_unicode = {v: k for k, v in emojis_text.items()}
