import logging
import requests
from model.artist import Artist
from model.album import Album
from model.track import Track
from service.filecache import cache_artist

logger = logging.getLogger(__name__)


def map_album(data) -> Album:
    # Maps iTunes collections to Album
    return Album(
        id=data["collectionId"],
        artist_id=data["artistId"],
        title=data["collectionName"],
        image_url=data["artworkUrl100"],
        genre=data["primaryGenreName"],
    )


def map_track(data) -> Track:
    # Maps iTunes discs and tracks to Track
    return Track(
        id=data["trackId"],
        name=data["trackName"],
        artist_id=data["artistId"],
        album_id=data["collectionId"],
        disc=data["discNumber"],
        number=data["trackNumber"],
        time_millis=data["trackTimeMillis"],
        preview_url=data.get("previewUrl"),
    )


# get artist by name
def get_artist(artist_name: str, limit: int) -> Artist:
    params: dict[str, str | int] = {
        "term": artist_name,
        "entity": "album",
        "limit": limit,
    }
    res = requests.get("https://itunes.apple.com/search", params=params)
    if res.status_code == 200:
        data = res.json()
        albums = data.get("results", [])
        if len(albums) > 0:
            artist_name = albums[0]["artistName"]
            artist_view_url = albums[0]["artistViewUrl"]
            artist_id = albums[0]["artistId"]
        logger.info(
            f"""Loaded {len(albums)} {
            artist_name} albums from iTunes"""
        )
        return Artist(
            artist_id, artist_name, artist_view_url, [map_album(x) for x in albums]
        )
    else:
        logger.error(
            f"""get_artist failed on {
            artist_name}: {res.status_code}"""
        )
        return Artist(0, artist_name, "", [])


# get tracks by album
def get_tracks(album: Album) -> None:
    params: dict[str, str | int] = {"id": album.id, "entity": "song"}
    res = requests.get("https://itunes.apple.com/lookup", params=params)
    if res.status_code == 200:
        data = res.json()
        tracks = data.get("results", [])[1:]
        logger.info(
            f"""Loaded {len(tracks)} tracks of {
                    album.title} from iTunes"""
        )
        album.tracks = [map_track(x) for x in tracks]
    else:
        logger.error(
            f"""get_tracks failed on {
            album.id}: {res.status_code}"""
        )
        album.tracks = []


# get albums by name
def get_albums(album_name: str, limit: int) -> list[Album]:
    params: dict[str, str | int] = {
        "term": album_name,
        "entity": "album",
        "limit": limit,
    }
    res = requests.get("https://itunes.apple.com/search", params=params)
    if res.status_code == 200:
        data = res.json()
        albums = data.get("results", [])
        logger.info(f"Loaded {len(albums)} albums from iTunes")
        return [map_album(x) for x in albums]
    else:
        logger.error(f"get_album failed on {album_name}: {res.status_code}")
        return []


# get tracks by name
def get_tracks_by_name(track_name: str, limit: int) -> list[Track]:
    params: dict[str, str | int] = {
        "term": track_name,
        "entity": "song",
        "limit": limit,
    }
    res = requests.get("https://itunes.apple.com/search", params=params)
    if res.status_code == 200:
        data = res.json()
        tracks = data.get("results", [])
        logger.info(f"Loaded {len(tracks)} tracks from iTunes")
        return [map_track(x) for x in tracks]
    else:
        logger.error(f"get_tracks_by_name failed on {track_name}: {res.status_code}")
        return []


@cache_artist
def search_artist(artist_name: str, limit: int) -> Artist:
    artist = get_artist(artist_name, limit)
    for album in artist.albums:
        get_tracks(album)
    return artist


def search_albums(album_name: str, limit: int) -> list[Album]:
    albums = get_albums(album_name, limit)
    for album in albums:
        get_tracks(album)
    return albums


def search_tracks(track_name: str, limit: int) -> list[Track]:
    return get_tracks_by_name(track_name, limit)
