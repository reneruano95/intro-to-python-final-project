import logging
import requests
from model.artist import Artist
from model.album import Album
from model.track import Track
from service.filecache import cache_artist

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
                 preview_url=data.get('previewUrl'))


def get_artist(artist_name: str, limit: int) -> Artist:
    params: dict[str, str | int] = {
        "term": artist_name,
        "entity": "album",
        "limit": limit
    }
    res = requests.get("https://itunes.apple.com/search", params=params)
    if res.status_code == 200:
        data = res.json()
        albums = data.get('results', [])
        if len(albums) > 0:
            artist_name = albums[0]["artistName"]
        logger.info(f"""Loaded {len(albums)} {
            artist_name} albums from iTunes""")
        return Artist(artist_name, [map_album(x) for x in albums])
    else:
        logger.error(f"""get_artist failed on {
            artist_name}: {res.status_code}""")
        return Artist(artist_name, [])


def get_tracks(album: Album) -> None:
    params: dict[str, str | int] = {
        "id": album.id,
        "entity": "song"
    }
    res = requests.get("https://itunes.apple.com/lookup", params=params)
    if res.status_code == 200:
        data = res.json()
        tracks = data.get("results", [])[1:]
        logger.info(f"""Loaded {len(tracks)} tracks of {
                    album.title} from iTunes""")
        album.tracks = [map_track(x) for x in tracks]
    else:
        logger.error(f"""get_tracks failed on {
            album.id}: {res.status_code}""")
        album.tracks = []


@cache_artist
def search_artist(artist_name: str, limit: int) -> Artist:
    artist = get_artist(artist_name, limit)
    for album in artist.albums:
        get_tracks(album)
    return artist
