import logging
import re
from typing import Optional, Union

import imdbinfo


logger = logging.getLogger("movienightbot")

imdb_url_regex = re.compile(r"title/tt([0-9]+)")

def get_imdb_info_by_id(imdb_id: Union[int, str]) -> Union[None, imdbinfo.services.MovieDetail]:
    if not imdb_id:
        return None

    return imdbinfo.get_movie(str(imdb_id))


def get_imdb_info(movie_name: str, kind: Optional[str] = None, year: Optional[int] = None) -> Union[None, imdbinfo.services.MovieDetail]:
    if not movie_name:
        return None

    if movie_name.lower().startswith("http"):
        movie_id = imdb_url_regex.findall(movie_name)
        logger.debug("movie regex: `{}` >> {}", movie_name, movie_id)
        if len(movie_id) == 1:
            imdb_id = movie_id[0]
        else:
            return None
    else:
        logger.debug(f"searching for `{movie_name}`")
        results = imdbinfo.search_title(movie_name)
        logger.debug("IMDB RESULTS: {}", str(results))
        for r in results.titles:
            if kind and kind != r.kind:
                continue
            if year and year != r.year:
                continue
            if r.title.lower() == movie_name.lower():
                logger.debug("{} Matched {}", movie_name, r)
                # Cant use r directly because it is a "MovieBriefInfo" object
                imdb_id = r.imdb_id
                break
        # for/else hell yeah!
        else:
            logger.debug("{} Unmatched", movie_name)
            return None

    return get_imdb_info_by_id(imdb_id)