from typing import List
from asyncio import sleep

import discord

from . import BaseAction
from ..db.controllers import MoviesController
from ..db.models import Movie


class SuggestedAction(BaseAction):
    action_name = "suggested"
    controller = MoviesController()

    def format_embed(self, movies: List[Movie], server_name: str, suggested_count) -> discord.Embed:
        embed = discord.Embed(
            title="Suggested Movies",
            description=f"{server_name} has {suggested_count} suggested movies",
        )
        for movie in movies:
            embed.add_field(
                name=movie.movie_name,
                value=f"{movie.suggested_on.date()} by {movie.suggested_by}",
            )
        return embed

    async def action(self, msg):
        suggested_movies = self.controller.get_suggested_for_server(msg.guild.id)
        suggested_count = len(suggested_movies)
        for chunk in range(0, len(suggested_movies), 25):
                # limit of 25 fields per embed, so send multiple messages if needed
                embed = self.format_embed(suggested_movies[chunk:chunk+25], msg.guild.name, suggested_count)
                await msg.author.send(content=None, embed=embed)
                await sleep(0.1)

    @property
    def help_text(self):
        return "Lists all movies that have been suggested."
