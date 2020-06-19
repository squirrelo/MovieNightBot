import peewee as pw

from . import BaseAction
from ..db.controllers import MoviesController, ServerController, IMDBInfoController
from ..util import get_imdb_info, cleanup_messages, capitalize_movie_name
from . import logger


class SuggestAction(BaseAction):
    action_name = "suggest"
    controller = MoviesController()
    server_controller = ServerController()
    imdb_controller = IMDBInfoController()

    async def action(self, msg):
        server_id = msg.guild.id
        server_row = self.server_controller.get_by_id(server_id)
        message_timeout = server_row.message_timeout
        if server_row.block_suggestions:
            server_msg = await msg.channel.send(
                "Suggestions are currently disabled on the server"
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
            return
        suggestion = capitalize_movie_name(self.get_message_data(msg))

        imdb_row = None
        if server_row.check_movie_names:
            imdb_info = get_imdb_info(suggestion)
            if not imdb_info:
                server_msg = await msg.channel.send(
                    "Could not find the movie title you suggested in IMDb."
                )
                if message_timeout > 0:
                    await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
                return

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
                # IMDB entry already added, so ignore error
                logger.debug(
                    "IMDB entry insert error: {}\n{}".format(imdb_data, str(e))
                )
                pass

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
            server_msg = await msg.channel.send(
                f"{suggestion} has already been suggested in this server."
            )
            if message_timeout > 0:
                await cleanup_messages([msg, server_msg], sec_delay=message_timeout)
            return
        server_msg = await msg.channel.send(
            f"Your suggestion of {suggestion} has been added to the list."
        )
        if message_timeout > 0:
            await cleanup_messages([msg, server_msg], sec_delay=message_timeout)

    @property
    def help_text(self):
        return (
            "Adds the supplied movie to the suggestions list. There is a chance this movie will now "
            "show up on future votes"
        )

    @property
    def help_options(self):
        return ["[movie name]"]
