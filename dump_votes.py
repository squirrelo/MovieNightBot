from argparse import ArgumentParser

from movienightbot.db import initialize_db
from movienightbot.db.controllers import MovieVoteController

parser = ArgumentParser()
parser.add_argument("--db", type=str, help="PeeWee URL to the SQLite database file")
parser.add_argument("--server", type=int, help="server id to look up a vote for")
args = parser.parse_args()

initialize_db(args.db)
movies = MovieVoteController().get_movies_for_server_vote(args.server)
if not movies:
    print("No vote currently going on for given server ID")
    exit(0)

for movie_vote in movies:
    print("{}: {}".format(movie_vote.movie.movie_name, movie_vote.score))
    for voter in movie_vote.user_votes:
        print("\t{}: {}".format(voter.user_name, voter.vote_rank))
