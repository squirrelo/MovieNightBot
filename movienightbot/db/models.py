import datetime

import peewee as pw
from . import BaseModel


class Server(BaseModel):
    id = pw.IntegerField(primary_key=True)
    channel = pw.IntegerField(null=False)
    movie_time = pw.TimeField(null=False, formats="%H:%M", default="12:00")
    admin_role = pw.TextField(null=False, default="Movie Master")
    tie_option = pw.TextField(null=False, default="breaker")
    num_movies_per_vote = pw.SmallIntegerField(null=False, default=8)
    num_votes_per_user = pw.SmallIntegerField(null=False, default=4)
    block_suggestions = pw.BooleanField(null=False, default=False)
    check_movie_names = pw.BooleanField(null=False, default=False)
    message_timeout = pw.SmallIntegerField(null=False, default=10)
    allow_tv_shows = pw.BooleanField(null=False, default=False)

    class Meta:
        table_name = "servers"


class IMDBInfo(BaseModel):
    imdb_id = pw.TextField(primary_key=True)
    title = pw.TextField(null=False)
    canonical_title = pw.TextField()
    year = pw.IntegerField()
    thumbnail_poster_url = pw.TextField()
    full_size_poster_url = pw.TextField()

    class Meta:
        table_name = "imdb_info"


class Movie(BaseModel):
    id = pw.AutoField(primary_key=True)
    server = pw.ForeignKeyField(Server, backref="movies")
    movie_name = pw.TextField(null=False)
    suggested_by = pw.TextField(null=False)
    last_score = pw.FloatField(null=True)
    num_votes_entered = pw.IntegerField(null=False, default=0)
    total_score = pw.FloatField(null=False, default=0.0)
    total_votes = pw.IntegerField(null=False, default=0)
    suggested_on = pw.TimestampField(
        utc=True, null=False, default=datetime.datetime.utcnow
    )
    watched_on = pw.TimestampField(utc=True, null=True, default=None)
    imdb_id = pw.ForeignKeyField(IMDBInfo, backref="movie_suggestions", null=True)

    class Meta:
        table_name = "movies"
        indexes = (
            # create a unique index on server and movie name
            (("server", "movie_name"), True),
        )


# Genre linked to Movie and not IMDBInfo because this allows non-IMDB servers to still manually add genres to movies
# and do votes by genre
class MovieGenre(BaseModel):
    movie_id = pw.ForeignKeyField(Movie, backref="movie_genres")
    genre = pw.TextField(null=False, index=True)

    class Meta:
        table_name = "movie_genre"
        indexes = (
            # create a unique index on movie and genre
            (("movie_id", "genre"), True),
        )


class Vote(BaseModel):
    """Tracks the actual vote going on in a server"""

    server_id = pw.ForeignKeyField(Server, backref="vote", primary_key=True)
    message_id = pw.IntegerField(
        null=True, help_text="The message ID holding the vote message on the server"
    )
    channel_id = pw.IntegerField(
        null=True, help_text="The channel ID holding the vote channel on the server"
    )

    class Meta:
        table_name = "votes"


class MovieVote(BaseModel):
    """Tracks the movies selected for voting on"""

    id = pw.AutoField(primary_key=True)
    vote = pw.ForeignKeyField(Vote, backref="movie_votes")
    movie = pw.ForeignKeyField(Movie, backref="+")
    score = pw.FloatField(null=False, default=0)
    emoji = pw.TextField(null=False)

    class Meta:
        tablename = "movie_votes"
        indexes = (
            # create a unique index on vote and movie
            (("vote", "movie"), True),
        )


class UserVote(BaseModel):
    """Tracks the ranked votes of a user"""

    id = pw.AutoField(primary_key=True)
    movie_vote = pw.ForeignKeyField(MovieVote, backref="user_votes")
    user_id = pw.IntegerField(null=False)
    user_name = pw.TextField(null=False)
    vote_rank = pw.SmallIntegerField(
        null=False,
        help_text="The numbered vote for the user, 1 is highest rank. Useful for ranked-choice voting",
    )

    class Meta:
        tablename = "user_votes"
        indexes = (
            # create a unique index on movie, user, and rank
            (("movie_vote", "user_id", "vote_rank"), True),
        )
