from pathlib import Path
from argparse import ArgumentParser
import logging

from .application import client
from .config import Config
from .db import initialize_db

arguments = ArgumentParser()
arguments.add_argument("-c", "--configfile", type=str, help="Path to the config file")
arguments.add_argument(
    "-l", "--loglevel", default="INFO", required=False, help="Logging level"
)
arguments.add_argument(
    "-f",
    "--logfile",
    default=None,
    required=False,
    help="path to save log file to. Leave blank for no logfile.",
)
args = arguments.parse_args()

log_level = getattr(logging, args.loglevel.upper())

logger = logging.getLogger("movienightbot")
logger.addHandler(logging.StreamHandler())
if args.logfile is not None:
    logger.addHandler(logging.FileHandler(args.logfile, mode="a"))
logger.setLevel(log_level)

config = Config.from_yaml(Path(args.configfile))
client.config = config
initialize_db(config.db_url)
client.run(config.token)
