import discord

from .db.controllers import ServerController, MovieVoteController


def build_vote_embed(server_id: int):
    server_row = ServerController.get_by_id(server_id)
    movie_rows = MovieVoteController.get_movies_for_server_vote(server_id)
    embed = discord.Embed(
        title="Movie Vote!", description="Use the emojis to vote on your preferred movies, in the order you would prefer them. "
                                         "If you need to reset your votes, use the :arrows_counterclockwise: emoji. "
                                         "To stop the vote, use the :stop sight: emoji.",
        timestamp=server_row.movie_time)
    for movie_vote in movie_rows:
        embed.add_field(
            name=f"{movie_vote.emoji} {movie_vote.movie.name}",
            value=f"Score: {movie_vote.score}",
            inline=True,
        )
    embed.set_footer(text=f"Movie time is {server_row.movie_time} UTC")
    return embed
