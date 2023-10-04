from pathlib import Path
from argparse import ArgumentParser
import logging
from threading import Thread

from .application import bot
from .config import Config
from .db import initialize_db
from .httpserver import run_webserver

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
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
for logger in (logging.getLogger("movienightbot"), logging.getLogger("peewee")):
    logger.addHandler(logging.StreamHandler())
    if args.logfile is not None:
        fh = logging.FileHandler(args.logfile, mode="a")
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=log_level,
    datefmt="%Y-%m-%d %H:%M:%S",
)

config = Config.from_yaml(Path(args.configfile))
bot.config = config
initialize_db(config.db_url)
thread = Thread(target=run_webserver, args=(config.port,), daemon=True)
thread.start()
bot.run(config.token)
