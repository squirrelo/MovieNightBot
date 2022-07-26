import pathlib
from typing import Dict, Any
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import logging
import json
import re

from movienightbot.db.controllers import (
    MoviesController,
    Movie,
    GenreController,
    VoteController,
    Vote,
    MovieVoteController,
    MovieVote,
    UserVoteController,
    UserVote,
)

logger = logging.getLogger("movienightbot")


class BotRequestHandler(BaseHTTPRequestHandler):
    suggested_json_regex = re.compile(r"^/json/suggested/[0-9]+$")
    watched_json_regex = re.compile(r"^/json/watched/[0-9]+$")
    vote_json_regex = re.compile(r"^/json/vote/[0-9]+$")
    suggested_regex = re.compile(r"^/suggested/[0-9]+$")
    watched_regex = re.compile(r"^/watched/[0-9]+$")
    vote_regex = re.compile(r"^/vote/[0-9]+$")
    static_regex = re.compile(r"^/static/.+$")
    favicon_url = "/favicon.ico"
    movies_controller = MoviesController()
    genre_controller = GenreController()
    vote_controller = VoteController()
    movie_vote_controller = MovieVoteController()
    user_vote_controller = UserVoteController()

    def set_json_headers(self, response_code: int = 200):
        self.send_response(response_code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def set_headers_by_extension(self, extension: str, response_code: int = 200):
        # Ensures that browsers won't block content if the content type isn't specified
        # Only bothering to add the types that get served
        self.send_response(response_code)
        if extension == ".css":
            self.send_header("Content-type", "text/css")
        elif extension == ".js":
            self.send_header("Content-type", "application/javascript")
        elif extension == ".ico":
            self.send_header("Content-type", "image/vnd.microsoft.icon")

        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def build_movie_base_info(self, movie: Movie) -> Dict[str, Any]:
        movie_info = {
            "title": movie.movie_name,
            "suggestor": movie.suggested_by,
            "date_suggested": str(movie.suggested_on.date()),
            "date_watched": str(movie.watched_on.date()) if movie.watched_on else None,
            "total_score": movie.total_score,
            "total_votes": movie.total_votes,
            "num_votes_entered": movie.num_votes_entered,
            "genre": None,
            "imdb_id": None,
            "year": None,
            "poster_url": None,
            "full_size_poster_url": None,
        }
        if movie.imdb_id:
            movie_info.update(
                {
                    "imdb_id": movie.imdb_id.imdb_id,
                    "year": movie.imdb_id.year,
                    "poster_url": movie.imdb_id.thumbnail_poster_url,
                    "full_size_poster_url": movie.imdb_id.full_size_poster_url,
                }
            )
        movie_genres = self.genre_controller.get_genres_by_movie_id(movie.id) or []
        genre_list = []
        for genre in movie_genres:
            genre_list.append(genre.genre)

        movie_info.update({"genre": genre_list})
        return movie_info

    def get_suggested_json(self, server_id: int):
        suggested_movies = self.movies_controller.get_suggested_for_server(server_id)
        suggestion_list = []
        for suggestion in suggested_movies:
            movie_info = self.build_movie_base_info(suggestion)
            suggestion_list.append(movie_info)

        self.set_json_headers()
        suggested = {"suggested": suggestion_list, "server_id": server_id}
        self.wfile.write(json.dumps(suggested).encode())

    def get_watched_json(self, server_id: int):
        watched_movies = self.movies_controller.get_watched_for_server(server_id)
        watched_list = []
        for watched in watched_movies:
            movie_info = self.build_movie_base_info(watched)
            watched_list.append(movie_info)

        self.set_json_headers()
        suggested = {"watched": watched_list, "server_id": server_id}
        self.wfile.write(json.dumps(suggested).encode())

    def get_vote_json(self, server_id: int):
        movies_vote_data = self.movie_vote_controller.get_movies_for_server_vote(server_id)
        movies_list = []
        for movie_vote in movies_vote_data:
            movie_info = self.build_movie_base_info(movie_vote.movie)
            movie_info.update({"score": movie_vote.score})
            movies_list.append(movie_info)

        self.set_json_headers()
        vote_info = {"movies": movies_list}
        self.wfile.write(json.dumps(vote_info).encode())

    def serve_html_movies(self):
        static_path = Path(Path(__file__).parent, "webfiles", "movies.html")
        with static_path.open("rb") as f:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read())

    def serve_html_vote(self):
        static_path = Path(Path(__file__).parent, "webfiles", "vote.html")
        with static_path.open("rb") as f:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read())

    def serve_static(self, path: str):
        static_parts = path.split("/")[2:]
        static_path = Path(Path(__file__).parent, "webfiles", *static_parts)
        # logger.debug("static_parts: {}".format(static_parts))
        # logger.debug("static_path: {}".format(static_path))
        if not static_path.exists():
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"")
            return

        with static_path.open("rb") as f:
            self.set_headers_by_extension(pathlib.Path(path).suffix)
            self.wfile.write(f.read())

    def get_server_id(self, path: str):
        return int(path.split("/")[-1])

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        if self.static_regex.match(path):
            self.serve_static(path)
        elif self.suggested_json_regex.match(path):
            server_id = self.get_server_id(path)
            self.get_suggested_json(server_id)
        elif self.watched_json_regex.match(path):
            server_id = self.get_server_id(path)
            self.get_watched_json(server_id)
        elif self.vote_json_regex.match(path):
            server_id = self.get_server_id(path)
            self.get_vote_json(server_id)
        elif self.suggested_regex.match(path):
            self.serve_html_movies()
        elif self.watched_regex.match(path):
            self.serve_html_movies()
        elif self.vote_regex.match(path):
            self.serve_html_vote()
        elif path == self.favicon_url:
            self.serve_static("/static/favicon.ico")
        else:
            self.set_json_headers(404)
            self.wfile.write(b"")

    def do_HEAD(self):
        self.set_json_headers()


def run_webserver(port: int = 8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, BotRequestHandler)
    logger.info("Starting webserver on port {}".format(port))
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv
    from movienightbot.db import initialize_db

    sql_url = argv[1]
    initialize_db(sql_url)
    run_webserver()
