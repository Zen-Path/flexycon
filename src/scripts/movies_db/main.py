#!{{@@ env['FLEXYCON_HOME'] @@}}/{{@@ d_venv_bin @@}}/python

# {{@@ header() @@}}

import argparse
import logging
import os
import time
from typing import Any, Literal

import requests
from dotenv import load_dotenv

from common.helpers import get_version
from common.io_utilities import write_dict_to_csv
from common.logger import log, setup_logging
from common.variables import FLEXYCON_HOME, FLEXYCON_SCRIPTS

load_dotenv(FLEXYCON_HOME / ".env")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Output files
OUTPUT_DIR = FLEXYCON_SCRIPTS / "movies_db" / "output"
MOVIES_CSV = OUTPUT_DIR / "movies.csv"
TV_SERIES_CSV = OUTPUT_DIR / "tv_series.csv"

MOVIE_CSV_COLUMNS = [
    # ("type", "Type"),
    ("title", "Title"),
    # ("status", "Status"),
    ("directors", "Directors"),
    ("main_cast", "Main Cast"),
    ("genres", "Genres"),
    ("runtime", "Runtime"),
    ("tmdb_rating", "TMDb Rating"),
    ("popularity", "Popularity"),
    ("imdb_id", "IMDb ID"),
    ("tmdb_id", "TMDb ID"),
    ("tmdb_url", "TMDb URL"),
    ("overview", "Overview"),
    ("release_date", "Release Date"),
    ("language", "Language"),
    ("origin_country", "Origin Country"),
    ("production_companies", "Production Companies"),
]

TV_SERIES_CSV_COLUMNS = [
    # ("type", "Type"),
    ("title", "Title"),
    ("status", "Status"),
    ("first_air_date", "First Air Date"),
    ("last_air_date", "Last Air Date"),
    ("seasons_count", "Seasons Count"),
    ("episodes_count", "Episodes Count"),
    ("creators", "Creators"),
    ("main_cast", "Main Cast"),
    ("genres", "Genres"),
    ("tmdb_rating", "TMBd Rating"),
    ("popularity", "Popularity"),
    ("imdb_id", "IMDb ID"),
    ("tmdb_id", "TMBd ID"),
    ("tmdb_url", "TMBd URL"),
    ("overview", "Overview"),
    ("language", "Language"),
    ("origin_country", "Origin Country"),
    ("networks", "Networks"),
]


def handle_genres(genres: list[dict[str, Any]]) -> str:
    unique_genres: set[str] = set()

    for g in genres:
        name = g.get("name", "")
        # Split by '&' to handle compound genres like "Sci-Fi & Fantasy"
        parts = name.split("&")
        for part in parts:
            # Clean, lowercase, and add to the set to ensure uniqueness
            cleaned = part.strip().lower()
            if cleaned:
                unique_genres.add(cleaned)

    return ", ".join(unique_genres)


def fetch_tmdb_raw_data(
    media_id: str | int, media_type: Literal["movie", "tv", "imdb"] = "imdb"
) -> dict[str, Any] | None:
    """Fetches raw TMDb data safely.

    - If `media_id` starts with 'tt' (IMDb ID), uses the /find endpoint.
    - If it's a TMDb numeric ID, requires explicit `media_type` ('movie' or
    'tv')
      to prevent ID collision bugs.
    """
    media_id_str = str(media_id).strip()

    # 1. Handle IMDb ID (Universally unique, safe to auto-detect via 'tt')
    if media_id_str.startswith("tt") or media_type == "imdb":
        url = f"https://api.themoviedb.org/3/find/{media_id_str}"
        params = {"api_key": TMDB_API_KEY, "external_source": "imdb_id"}
        log.info(f"Fetching data for IMDb ID {media_id_str!r}")

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching IMDb ID {media_id_str}: {response.status_code}")
            return None

    # 2. Handle TMDb Movie ID explicitly
    elif media_type == "movie":
        url = f"https://api.themoviedb.org/3/movie/{media_id_str}"
        params = {"api_key": TMDB_API_KEY}
        log.info(f"Fetching movie data for TMDb ID {media_id_str!r}")

        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Wrap in the same structure so route_media_type() remains compatible
            return {"movie_results": [response.json()], "tv_results": []}
        else:
            print(
                f"Error fetching TMDb Movie ID {media_id_str}: {response.status_code}"
            )
            return None

    # 3. Handle TMDb TV Series ID explicitly
    elif media_type == "tv":
        url = f"https://api.themoviedb.org/3/tv/{media_id_str}"
        params = {"api_key": TMDB_API_KEY}
        log.info(f"Fetching tv data for TMDb ID {media_id_str!r}")

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return {"movie_results": [], "tv_results": [response.json()]}
        else:
            print(f"Error fetching TMDb TV ID {media_id_str}: {response.status_code}")
            return None


def process_movie_metadata(
    tmdb_id: str, overview_meta: dict[str, Any]
) -> dict[str, Any] | None:
    """Processes movie details and writes to movies.csv."""
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "append_to_response": "credits"}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        log.error(f"Failed to fetch details for movie ID {tmdb_id}")
        return None

    details = response.json()
    log.debug(details)

    result: dict[str, Any] = {}

    result["type"] = overview_meta.get("media_type", "")
    result["status"] = details.get("status", "").lower()

    result["release_date"] = details.get("release_date")
    result["title"] = (
        f"{details.get('title', '').strip('“').rstrip('”')} ({result['release_date'][:4]})"
    )
    result["genres"] = handle_genres(details.get("genres", []))

    result["runtime"] = details.get("runtime")

    # Extract directors
    crew = details.get("credits", {}).get("crew", [])
    directors = [p["name"] for p in crew if p.get("job") == "Director"]
    result["directors"] = ", ".join(directors) if directors else "N/A"

    cast = details.get("credits", {}).get("cast", [])
    result["main_cast"] = ", ".join([actor["name"] for actor in cast[:5]])

    result["tmdb_rating"] = round(details.get("vote_average", 0), 1)

    result["imdb_id"] = details.get("imdb_id", 0)
    result["tmdb_id"] = details.get("id", 0)
    result["tmdb_url"] = (
        f"https://www.themoviedb.org/movie/{result['tmdb_id']}"
        if result["tmdb_id"]
        else ""
    )

    result["popularity"] = round(details.get("popularity", 0), 0)
    result["overview"] = details.get("overview", "")
    result["language"] = details.get("original_language", "")
    result["origin_country"] = details.get("origin_country", [])[0]

    # Extract production companies
    production_companies = details.get("production_companies", {})
    companies_names = [p["name"] for p in production_companies]
    result["production_companies"] = (
        ", ".join(companies_names) if companies_names else "N/A"
    )

    return result


def process_tv_metadata(
    tmdb_id: str, overview_meta: dict[str, Any]
) -> dict[str, Any] | None:
    """Processes TV series details and writes to tv_series.csv."""
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "append_to_response": "credits,external_ids",
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        log.error(f"Failed to fetch details for TV series ID {tmdb_id}")
        return None

    details = response.json()
    log.debug(details)

    result: dict[str, Any] = {}

    result["type"] = overview_meta.get("media_type", "")
    result["status"] = details.get("status", "").lower()

    result["first_air_date"] = details.get("first_air_date") or ""
    result["last_air_date"] = details.get("last_air_date") or ""

    result["title"] = (
        f"{details.get('name', '').strip('“').rstrip('”')} ({result['first_air_date'][:4]})"
    )
    result["genres"] = handle_genres(details.get("genres", []))

    result["seasons_count"] = details.get("number_of_seasons", 0)
    result["episodes_count"] = details.get("number_of_episodes", 0)

    # Extract creators
    creators = [c["name"] for c in details.get("created_by", [])]
    result["creators"] = ", ".join(creators) if creators else "N/A"

    cast = details.get("credits", {}).get("cast", [])
    result["main_cast"] = ", ".join([actor["name"] for actor in cast[:5]])

    result["runtime"] = ""
    result["tmdb_rating"] = round(details.get("vote_average", 0), 1)

    result["imdb_id"] = details.get("external_ids", {}).get("imdb_id") or ""
    result["tmdb_id"] = details.get("id", 0)
    result["tmdb_url"] = (
        f"https://www.themoviedb.org/tv/{result['tmdb_id']}"
        if result["tmdb_id"]
        else ""
    )

    result["popularity"] = round(details.get("popularity", 0), 0)
    result["overview"] = details.get("overview", "")
    result["language"] = details.get("original_language", "")
    result["origin_country"] = details.get("origin_country", [])[0]

    # Extract production companies
    networks = details.get("networks", {})
    networks_names = [p["name"] for p in networks]
    result["networks"] = ", ".join(networks_names) if networks_names else "N/A"

    return result


def build_parser() -> argparse.ArgumentParser:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        prog="movies_db",
        description="Fetch movie and tv series data to be used in Google Sheets.",
    )

    # parser.add_argument(
    #     "tmdb_ids", nargs="+", type=int, help="list of TBMd ids to fetch"
    # )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    setup_logging(log, logging.DEBUG if args.verbose else logging.INFO)
    log.debug(args)

    raw_ids = """\
tt123
"""
    clean_ids = set([media_id.strip() for media_id in raw_ids.split("\n") if media_id])

    movies: list[dict[str, Any]] = []
    tv_series: list[dict[str, Any]] = []

    for media_id in clean_ids:
        raw_data = fetch_tmdb_raw_data(media_id, "tv")
        if not raw_data:
            continue

        movie_results = raw_data.get("movie_results", [])
        tv_results = raw_data.get("tv_results", [])

        if movie_results:
            item = movie_results[0]
            result = process_movie_metadata(item["id"], item)
            if result:
                movies.append(result)

        elif tv_results:
            item = tv_results[0]
            series = process_tv_metadata(item["id"], item)

            if series:
                tv_series.append(series)

        else:
            log.warning(
                f"No matching movie or TV series found in TMDb for IMDb ID: {media_id}"
            )

        time.sleep(0.1)

    if movies:
        write_dict_to_csv(movies, filename=MOVIES_CSV, csv_columns=MOVIE_CSV_COLUMNS)

    if tv_series:
        write_dict_to_csv(tv_series, TV_SERIES_CSV, TV_SERIES_CSV_COLUMNS)


if __name__ == "__main__":
    main()
