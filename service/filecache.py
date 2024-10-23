import json
import logging
from dataclasses import asdict
from model.artist import Artist
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


def get_artist_path(artist_name: str, limit: int) -> Path:
    """Gets the path to a cache file for the given artist name and limit.

    Args:
        artist_name (str): artist name
        limit (int): number of albums to cache

    Returns:
        Path: file path for the albums cache file
    """
    return Path(f"./appcache/{artist_name.replace(' ', '-')}-{limit}.json".lower())


def save_artist(artist: Artist):
    """Utility function used to cache albums that have been downloaded.

    Args:
        artist_name (str): the artist name
        albums (List[Album]): the list of albums to cache
    """

    n = len(artist.albums)
    # don't cache if no albums are found
    if n == 0:
        return
    # don't cache if albums with no tracks are found
    albums_with_tracks = [
        album for album in artist.albums if album.tracks and len(album.tracks) > 0]
    if n != len(albums_with_tracks):
        return

    path = get_artist_path(artist.name, n)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as file:
        json.dump({"name": artist.name, "albums": [
                  asdict(album) for album in artist.albums]}, file, indent=2)
    logger.info(f"Cached {n} {artist.name} albums")


def cache_artist(fn: Callable[[str, int], Artist]) -> Callable[[str, int], Artist]:
    """Decorator to cache the results of an Artist service.

    Args:
        fn (Callable[[str, int], Artist]): service function to cache.

    Returns:
        Callable[[str, int], Artist]: wrapped service function.
    """
    def wrapper(artist_name: str, limit: int) -> Artist:
        path = get_artist_path(artist_name, limit)

        # Check if the cached file exists
        if path.exists():
            with path.open("r") as file:
                # Load from cache and return a cached Artist instance
                data = json.load(file)
                artist = Artist(**data)
                logger.info(f"""Loaded {len(artist.albums)} {
                            artist.name} albums from cache""")
                return artist
        else:
            # Call the original function if no cache is found
            artist = fn(artist_name, limit)
            # Save the artist result to cache
            save_artist(artist)
            # Return the fetched Artist
            return artist

    return wrapper
