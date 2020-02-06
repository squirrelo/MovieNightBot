from typing import List

import discord

from . import BaseAction
from ..db.controllers import MoviesController
from ..db.models import Movie


class SuggestedAction(BaseAction):
    action_name = "suggested"
    controller = MoviesController()

    def format_embed(self, movies: List[Movie], server_name: str):
        embed = discord.Embed(
            title="Suggested Movies",
            description=f"{server_name} has {len(movies)} suggested movies",
        )
        for movie in movies:
            embed.add_field(
                name=movie.movie_name,
                value=f"{movie.suggested_on.date()} by {movie.suggested_by}",
            )
        return embed

    async def action(self, msg):
        if msg.guild is None:
            await msg.author.send("You can't do this command from a DM!")
            return
        suggested_movies = self.controller.get_suggested_for_server(msg.guild.id)
        embed = self.format_embed(suggested_movies, msg.guild.name)
        await msg.author.send(content=None, embed=embed)

    @property
    def help_text(self):
        return "Lists all movies that have been suggested."
