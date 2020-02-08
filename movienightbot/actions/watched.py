from typing import List
from asyncio import sleep

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
        for chunk in range(0, len(watched_movies), 25):
            # limit of 25 fields per embed, so send multiple messages if needed
            embed = self.format_embed(watched_movies[chunk:chunk + 25], msg.guild.name)
            await msg.author.send(content=None, embed=embed)
            await sleep(0.1)

    @property
    def help_text(self):
        return "Lists all movies that have been watched."
