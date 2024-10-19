import json
import logging
from pathlib import Path
from typing import List
from model.album import Album
from model.track import Track
from service.AlbumService import AlbumService

logger = logging.getLogger(__name__)


def get_albums_path(artist_name: str, limit: int) -> Path:
    """Builds the file name for the albums cache file.

    Args:
        artist_name (str): artist name
        limit (int): number of albums to cache

    Returns:
        Path: file path for the albums cache file
    """
    return Path(f"./appcache/{artist_name.replace(' ', '-')}-{limit}.json")


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
    logger.info(f"Loaded {len(albums)} albums from cache")
    return albums


class FileCacheAlbumService(AlbumService):
    """File cache adapter for the AlbumService.

    Args:
        AlbumService (_type_): AlbumService superclass
    """

    async def get_albums(self, artist_name: str, limit: int):
        path = get_albums_path(artist_name, limit)
        with path.open("r") as file:
            return map_albums(json.load(file))

    async def get_tracks(self, _):
        pass


def cache_albums(artist_name: str, albums: List[Album]):
    """Utility function used to cache albums that have been downloaded.

    Args:
        artist_name (str): the artist name
        albums (List[Album]): the list of albums to cache
    """

    if len(albums) == 0:
        return
    albums_with_tracks = [
        album for album in albums if album.tracks and len(album.tracks) > 0]
    if len(albums) != len(albums_with_tracks):
        return

    data = [album.to_dict() for album in albums]
    path = get_albums_path(artist_name, len(albums))
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as file:
        json.dump(data, file, indent=4)
    logger.info(f"Cached {len(albums)} {artist_name} albums")
