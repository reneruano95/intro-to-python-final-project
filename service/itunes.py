import logging
import requests
from typing import List, cast

import requests.structures
from model.album import Album
from model.track import Track
from service.AlbumService import AlbumService

logger = logging.getLogger(__name__)


def map_album(data) -> Album:
    # Maps iTunes collections to Album
    return Album(id=data['collectionId'],
                 title=data['collectionName'],
                 image_url=data['artworkUrl100'])


def map_track(data) -> Track:
    # Maps iTunes discs and tracks to Track
    return Track(name=data['trackName'],
                 disc=data['discNumber'],
                 number=data['trackNumber'],
                 time_millis=data['trackTimeMillis'],
                 preview_url=data['previewUrl'])


class iTunesAlbumService(AlbumService):
    def get_albums(self, artist_name: str, limit: int):
        params: dict[str, str | int] = {
            "term": artist_name,
            "entity": "album",
            "limit": limit
        }
        res = requests.get("https://itunes.apple.com/search", params)
        if res.status_code == 200:
            data = res.json()
            albums = data.get('results', [])
            logger.info(f"""Loaded {len(albums)} {
                artist_name} albums from iTunes""")
            return [map_album(x) for x in albums]
        else:
            logger.error(f"""get_albums failed on {
                         artist_name}: {res.status_code}""")
            return cast(List[Album], [])

    def get_tracks(self, album_id: int):
        params: dict[str, str | int] = {
            "id": album_id,
            "entity": "song"
        }
        res = requests.get("https://itunes.apple.com/lookup", params)
        if res.status_code == 200:
            data = res.json()
            tracks = data.get("results", [])[1:]
            logger.info(f"Loaded {len(tracks)} tracks from iTunes")
            return [map_track(x) for x in tracks]
        else:
            logger.error(f"get_tracks failed on {album_id}: {res.status_code}")
            return cast(List[Track], [])
