from . import BaseAction
from ..db.controllers import MoviesController, ServerController, GenreController
from ..util import cleanup_messages, capitalize_movie_name


class SetGenre(BaseAction):
    action_name = "set_genre"
    admin = False
    controller = MoviesController()
    server_controller = ServerController()
    genre_controller = GenreController()

    async def action(self, msg):
        server_id = msg.guild.id
        server_row = self.server_controller.get_by_id(server_id)
        message_timeout = server_row.message_timeout
        genre, movie_name = self.get_message_data(msg, data_parts=2)
        genre = genre.lower()
        movie_name = capitalize_movie_name(movie_name)
        self.genre_controller.add_genre_to_movie(server_id, movie_name, genre)

        server_msg = await msg.channel.send(
            f"Movie {movie_name} has been updated with genre {genre}"
        )
        await cleanup_messages([msg, server_msg], sec_delay=message_timeout)

    @property
    def help_text(self):
        return "Adds a genre to a movie manually. Genre must be a single word or contiguous block, like `Sci-Fi`"

    @property
    def help_options(self):
        return ["[genre]", "[movie_name]"]
