from typing import List

import discord

from . import BaseAction
from ..db.controllers import MoviesController
from ..db.models import Movie


class WatchedAction(BaseAction):
    action_name = "watched"
    controller = MoviesController()

    def format_embed(self, movies: List[Movie], server_name: str):
        embed = discord.Embed(
            title="Suggested Movies",
            description=f"{server_name} has watched {len(movies)} movies so far",
        )
        for movie in movies:
            embed.add_field(
                name=movie.movie_name, value=f"Watched {movie.watched_on.date()}"
            )
        return embed

    async def action(self, msg):
        watched_movies = self.controller.get_watched_for_server(msg.guild.id)
        embed = self.format_embed(watched_movies, msg.guild.name)
        await msg.author.send(content=None, embed=embed)

    @property
    def help_text(self):
        return "Lists all movies that have been watched."
