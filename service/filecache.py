from typing import Coroutine, Callable
import json
import logging
from pathlib import Path
from typing import Coroutine, List
from model.artist import Artist
from model.album import Album
from model.track import Track

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


def map_albums(artist_data) -> List[Album]:
    """Maps the data from the cache file to the Album model.

    Args:
        artist_data (_type_): artist data from the cache file

    Returns:
        List[Album]: list of albums
    """
    albums: List[Album] = []
    for album_data in artist_data:
        tracks = album_data['tracks']
        album = Album(id=album_data['id'], title=album_data['title'],
                      image_url=album_data['image_url'])
        album.tracks = [Track(name=track_data['name'],
                              disc=track_data['disc'],
                              number=track_data['number'],
                              time_millis=track_data['time_millis'],
                              preview_url=track_data['preview_url']) for track_data in tracks]
        albums.append(album)
    return albums


def save_artist(artist: Artist):
    """Utility function used to cache albums that have been downloaded.

    Args:
        artist_name (str): the artist name
        albums (List[Album]): the list of albums to cache
    """

    n = len(artist.albums)
    if n == 0:
        return
    albums_with_tracks = [
        album for album in artist.albums if album.tracks and len(album.tracks) > 0]
    # don't cache if albums with no tracks are found
    if n != len(albums_with_tracks):
        return

    data = [album.to_dict() for album in artist.albums]
    path = get_artist_path(artist.name, n)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as file:
        json.dump(data, file, indent=4)
    logger.info(f"Cached {n} {artist.name} albums")


def cache_artist(fn: Callable[[str, int], Coroutine[None, None, Artist]]) -> Callable[[str, int], Coroutine[None, None, Artist]]:
    """Decorator to cache the results of an Artist service.

    Args:
        fn (Callable[[str, int], Coroutine]): service function to cache.

    Returns:
        Callable[[str, int], Coroutine]: wrapped service function.
    """
    async def wrapper(artist_name: str, limit: int) -> Artist:
        path = get_artist_path(artist_name, limit)
        print(path)

        # Check if the cached file exists
        if path.exists():
            with path.open("r") as file:
                # Load from cache and return a cached Artist instance
                cached_data = json.load(file)
                artist = Artist(artist_name, map_albums(cached_data))
                logger.info(f"""Loaded {len(artist.albums)} {
                            artist.name} albums from cache""")
                return artist
        else:
            # Call the original function if no cache is found
            artist = await fn(artist_name, limit)

            # Save the artist result to cache
            save_artist(artist)

            # Return the fetched Artist
            return artist

    return wrapper
