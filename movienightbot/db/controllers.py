from typing import List, Union, Dict, Any
from string import ascii_lowercase
from collections import defaultdict
import logging

import peewee as pw
import discord

from .models import Server, Movie, Vote, MovieVote, UserVote
from . import BaseController

logger = logging.getLogger("movienightbot")


class ServerController(BaseController):
    model = Server


class MoviesController(BaseController):
    model = Movie

    def get_by_server_and_id(self, server_id: int, movie: str) -> Movie:
        return (
            Movie.select()
            .where((Movie.server == server_id) & (Movie.movie_name == movie))
            .get()
        )

    def get_watched_for_server(self, server_id: int) -> List[Movie]:
        return (
            Movie.select()
            .order_by(Movie.movie_name)
            .where((Movie.server == server_id) & Movie.watched_on.is_null(False))
            .execute()
        )

    def get_suggested_for_server(self, server_id: int) -> List[Movie]:
        return (
            Movie.select()
            .order_by(Movie.movie_name)
            .where((Movie.server == server_id) & Movie.watched_on.is_null())
            .execute()
        )


def movie_score_weightings(server_id: int):
    num_votes_allowed = ServerController().get_by_id(server_id).num_votes_per_user
    scores_dict = defaultdict(float)
    scores = [
        round((1 / num_votes_allowed) * x, 2) for x in range(1, num_votes_allowed + 1)
    ][::-1]
    scores_dict.update({x + 1: s for x, s in enumerate(scores)})
    return scores_dict


class VoteController(BaseController):
    model = Vote

    def get_by_id(self, server_id: int) -> Union[Vote, None]:
        return super().get_by_id(id=server_id, primary_key="server_id")

    def start_vote(self, server_id: int) -> Vote:
        with self.transaction():
            server_row = ServerController().get_by_id(server_id)
            num_movies = server_row.num_movies_per_vote
            movies_for_vote = (
                Movie.select()
                .order_by(pw.fn.Random())
                .where((Movie.server == server_id) & Movie.watched_on.is_null(True))
                .limit(num_movies)
            )
            vote_row = self.create({"server_id": server_id})
            movie_vote_controller = MovieVoteController()
            for movie, emoji_letter in zip(movies_for_vote, ascii_lowercase):
                movie_vote_controller.create(
                    {
                        "vote": vote_row,
                        "movie": movie,
                        "emoji": f":regional_indicator_{emoji_letter}:",
                    }
                )
        return vote_row

    def start_runoff_vote(
        self, server_id: int, vote_message: discord.Message, movies: List[Movie]
    ) -> Vote:
        with self.transaction():
            vote_row = self.create(
                {
                    "server_id": server_id,
                    "channel_id": vote_message.channel.id,
                    "message_id": vote_message.id,
                }
            )
            movie_vote_controller = MovieVoteController()
            for movie, emoji_letter in zip(movies, ascii_lowercase):
                movie_vote_controller.create(
                    {
                        "vote": vote_row,
                        "movie": movie,
                        "emoji": f":regional_indicator_{emoji_letter}:",
                    }
                )
        return vote_row

    def set_message_id(self, server_id: int, message_id: int) -> Vote:
        vote_row = self.get_by_id(server_id)
        vote_row.message_id = message_id
        vote_row = self.update(vote_row)
        return vote_row

    def end_vote(self, server_id: int) -> List[Movie]:
        with self.transaction():
            vote_data = self.get_by_id(server_id)
            movie_votes = vote_data.movie_votes
            best_score = max(m.score for m in movie_votes)
            movies = []
            for movie_vote in movie_votes:
                # set the last score for all movies
                movie = movie_vote.movie
                movie.last_score = movie_vote.score
                movie.num_votes_entered += 1
                movie.total_score += movie_vote.score
                movie.total_votes += len(movie_vote.user_votes)
                movie.save()
                # create the list of best scored movies in case of tie
                if movie_vote.score == best_score:
                    movies.append(movie_vote.movie)
            self.delete(vote_data, recursive=True)
        return movies


class MovieVoteController(BaseController):
    model = MovieVote

    def convert_emoji(self, server_id: int, emoji: str) -> MovieVote:
        return (
            MovieVote.select()
            .join(Vote)
            .where((Vote.server_id == server_id) & (MovieVote.emoji == emoji))
            .get()
        )

    def get_movies_for_server_vote(self, server_id: int) -> List[MovieVote]:
        with self.transaction():
            vote_row = VoteController().get_by_id(server_id)
            if vote_row:
                # Lazy eval, so force it to eval into a list
                movies = [x for x in vote_row.movie_votes]
            else:
                movies = []
        return movies

    def get_score_for_movie(self, server_id: int, movie: str) -> float:
        return (
            MovieVote.select("score")
            .join(Vote)
            .where((MovieVote.movie == movie) & (Vote.server_id == server_id))
            .get()
            .score
        )


class UserVoteController(BaseController):
    model = UserVote

    def create(self, row_data: Dict[str, Any]):
        with self.transaction():
            user_vote = super().create(row_data)
            # Add score to movie
            movie_vote = user_vote.movie_vote
            scores = movie_score_weightings(server_id=movie_vote.vote.server_id)
            logger.debug(f"Rank: {user_vote.vote_rank}")
            logger.debug(f"Scores: {scores}")
            movie_vote.score += scores[user_vote.vote_rank]
            movie_vote.save()
            logger.debug(
                f"added {scores[user_vote.vote_rank]} to MovieVote {movie_vote.id}, new score {movie_vote.score}"
            )
        return user_vote

    def reset_user_votes(self, server_id: int, user_id: int) -> List[MovieVote]:
        with self.transaction():
            scores = movie_score_weightings(server_id=server_id)
            user_votes = self.get_by_server_and_user(server_id, user_id)
            movie_votes = [u.movie_vote for u in user_votes]
            # remove user score for each movie, then the user vote row
            movie_vote_controller = MovieVoteController()
            for user_vote_row in user_votes:
                movie_vote = user_vote_row.movie_vote
                movie_vote.score -= scores[user_vote_row.vote_rank]
                movie_vote_controller.update(movie_vote)
                self.delete(user_vote_row)
        return movie_votes

    def get_by_server_and_user(self, server_id: int, user_id: int) -> List[UserVote]:
        return [
            x
            for x in UserVote.select()
            .join(MovieVote)
            .join(Vote)
            .where((Vote.server_id == server_id) & (UserVote.user_id == user_id))
        ]

    def get_next_rank(self, server_id: int, user_id: int) -> int:
        max_rank = (
            UserVote.select(pw.fn.MAX(UserVote.vote_rank))
            .join(MovieVote)
            .join(Vote)
            .where((Vote.server_id == server_id) & (UserVote.user_id == user_id))
            .scalar()
        )
        return max_rank + 1 if max_rank else 1

    def register_vote(self, user_id: int, movie_vote: MovieVote) -> UserVote:
        with self.transaction():
            server_id = movie_vote.vote.server_id
            next_rank = self.get_next_rank(server_id, user_id)
            vote_data = {
                "movie_vote": movie_vote,
                "user_id": user_id,
                "vote_rank": next_rank,
            }
            logger.debug(f"Registering new vote: {vote_data}")
            self.create(vote_data)

    def remove_vote(self, user_id: int, movie_vote: MovieVote) -> None:
        with self.transaction():
            server_id = movie_vote.vote.server_id
            user_votes = self.get_by_server_and_user(server_id, user_id)
            scores = movie_score_weightings(server_id=movie_vote.vote.server_id)
            # First look for the movie being deleted, and see if it even was voted for.
            # If so, delete it
            for user_vote in user_votes:
                if user_vote.movie_vote == movie_vote:
                    removed_rank = user_vote.vote_rank
                    self.delete(user_vote)
                    user_votes.remove(user_vote)
                    # Update movie score
                    movie_vote = user_vote.movie_vote
                    movie_vote.score -= scores[removed_rank]
                    movie_vote.save()
                    break
            else:
                return
            # Reset the rankings of all other votes as necessary
            for user_vote in user_votes:
                if user_vote.vote_rank > removed_rank:
                    # Subtract original score and add new score to update the movie's total score
                    movie_vote = user_vote.movie_vote
                    movie_vote.score = (
                        movie_vote.score
                        - scores[user_vote.vote_rank]
                        + scores[user_vote.vote_rank - 1]
                    )
                    user_vote.vote_rank -= 1
                    user_vote.save()
                    movie_vote.save()
