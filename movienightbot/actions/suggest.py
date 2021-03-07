from typing import Union
import peewee as pw

from . import BaseAction
from ..db.controllers import (
    MoviesController,
    ServerController,
    IMDBInfoController,
    IMDBInfo,
)
from ..util import get_imdb_info, capitalize_movie_name
from . import logger


class SuggestAction(BaseAction):
    action_name = "suggest"
    controller = MoviesController()
    server_controller = ServerController()
    imdb_controller = IMDBInfoController()

    def imdb_data(self, msg) -> Union[None, IMDBInfo]:
        suggestion = capitalize_movie_name(self.get_message_data(msg))
        imdb_info = get_imdb_info(suggestion)
        if not imdb_info:
            return None
        # see if the row already exists
        try:
            imdb_row = self.imdb_controller.get_by_id(imdb_info.movieID)
        except pw.DoesNotExist:
            pass
        else:
            return imdb_row
        # row doesnt exist, so add it
        imdb_data = {
            "imdb_id": imdb_info.movieID,
            "title": imdb_info["title"],
            "canonical_title": imdb_info["canonical title"],
            "year": imdb_info["year"],
            "thumbnail_poster_url": imdb_info["cover url"],
            "full_size_poster_url": imdb_info["full-size cover url"],
        }
        try:
            imdb_row = self.imdb_controller.create(imdb_data)
        except pw.IntegrityError as e:
            logger.error("IMDB entry insert error: {}\n{}".format(imdb_data, str(e)))
            return None
        return imdb_row

    async def action(self, msg):
        server_id = msg.guild.id
        server_row = self.server_controller.get_by_id(server_id)
        message_timeout = server_row.message_timeout
        if server_row.block_suggestions:
            msg_data = {
                "content": "Suggestions are currently disabled on the server",
            }
            if message_timeout > 0:
                msg_data["delete_after"] = message_timeout
                msg_data["also_delete"] = [msg]

            return (msg.channel, msg_data)

        if server_row.check_movie_names:
            imdb_row = self.imdb_data(msg)
            suggestion = (
                capitalize_movie_name(imdb_row.title)
                if imdb_row
                else capitalize_movie_name(self.get_message_data(msg))
            )
            if imdb_row is None:
                msg_data = {
                    "content": "Could not find the movie title you suggested in IMDb.",
                }
                if message_timeout > 0:
                    msg_data["delete_after"] = message_timeout
                    msg_data["also_delete"] = [msg]
                return (msg.channel, msg_data)
        else:
            imdb_row = None
            suggestion = capitalize_movie_name(self.get_message_data(msg))

        movie_data = {
            "server": server_id,
            "movie_name": suggestion,
            "suggested_by": msg.author.name,
            "imdb_id": imdb_row,
        }
        try:
            self.controller.create(movie_data)
        except pw.IntegrityError as e:
            logger.debug("Movie insert error: {}\n{}".format(movie_data, str(e)))
            msg_data = {
                "content": f"{suggestion} has already been suggested in this server.",
            }
            if message_timeout > 0:
                msg_data["delete_after"] = message_timeout
                msg_data["also_delete"] = [msg]
            return (msg.channel, msg_data)
        imdb_year = f"({imdb_row.year}) " if imdb_row else ""
        msg_data = {
            "content": f"Your suggestion of {suggestion} {imdb_year}has been added to the list.",
        }
        if message_timeout > 0:
            msg_data["delete_after"] = message_timeout
            msg_data["also_delete"] = [msg]
        return (msg.channel, msg_data)

    @property
    def help_text(self):
        return (
            "Adds the supplied movie to the suggestions list. There is a chance this movie will now "
            "show up on future votes"
        )

    @property
    def help_options(self):
        return ["[movie name]"]
