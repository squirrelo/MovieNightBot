from abc import ABC
from typing import Any, List, Union

import peewee as pw

from .models import Server, Movie, Vote, MovieVote, UserVote
from . import BaseController


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
    return {x: 1 / num_votes_allowed for x in range(1, num_votes_allowed + 1)}


class VoteController(BaseController):
    model = Vote

    def get_by_id(self, server_id: int) -> Union[Vote, None]:
        return super().get_by_id(id=server_id, primary_key="server_id")

    def start_vote(self, server_id: int) -> Vote:
        raise NotImplementedError


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
        vote_row = self.get_vote_for_server(server_id)
        if vote_row:
            return vote_row.movie_votes
        else:
            return []

    def get_score_for_movie(self, server_id: int, movie: str) -> float:
        return (
            MovieVote.select("score")
            .join(Vote)
            .where((MovieVote.movie == movie) & (Vote.server_id == server_id))
            .get()
        )


class UserVoteController(BaseController):
    model = UserVote

    def create(self, **kwargs):
        with self.transaction():
            user_vote = super().create(**kwargs)
            # Add score to movie
            movie_vote = user_vote.movie_vote
            scores = movie_score_weightings(server_id=movie_vote.vote.server_id)
            movie_vote.score += scores[user_vote.vote_rank]
            movie_vote.save()
        return user_vote

    def reset_user_votes(self, server_id: int, user_id: int) -> None:
        UserVote.delete().join(MovieVote).join(Vote).where(
            (Vote.server_id == server_id) & UserVote.user_id == user_id
        )

    def get_by_server_and_user(self, server_id: int, user_id: int) -> List[UserVote]:
        return (
            UserVote.select()
            .join(MovieVote)
            .join(Vote)
            .where((Vote.server_id == server_id) & UserVote.user_id == user_id)
        )

    def get_next_rank(self, server_id: int, user_id: int) -> int:
        user_votes = self.get_by_server_and_user(server_id, user_id)
        return max(user_votes.vote_rank) + 1

    def register_vote(self, user_id: int, movie_vote: MovieVote) -> UserVote:
        with self.transaction():
            server_id = movie_vote.vote[0].server_id
            next_rank = self.get_next_rank(server_id, user_id)
            self.create(
                {"movie_vote": movie_vote, "user_id": user_id, "vote_rank": next_rank}
            )

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
