import logging
import requests
from model.artist import Artist
from model.album import Album
from model.track import Track
from service.filecache import cache_artist

logger = logging.getLogger(__name__)


def map_artist(data) -> Artist:
    # Maps iTunes artists to Artist
    return Artist(
        id=data["artistId"],
        name=data["artistName"],
    )


def map_album(data) -> Album:
    # Maps iTunes collections to Album
    return Album(
        id=data["collectionId"],
        artist_id=data["artistId"],
        artist_name=data["artistName"],
        title=data["collectionName"],
        image_url=data["artworkUrl100"],
        genre=data["primaryGenreName"],
        release_date=data["releaseDate"],
    )


def map_track(data) -> Track:
    # Maps iTunes discs and tracks to Track
    return Track(
        id=data["trackId"],
        name=data["trackName"],
        artist_id=data["artistId"],
        artist_name=data["artistName"],
        album_id=data["collectionId"],
        album_name=data["collectionName"],
        disc=data["discNumber"],
        number=data["trackNumber"],
        genre=data["primaryGenreName"],
        release_date=data["releaseDate"],
        time_millis=data["trackTimeMillis"],
        preview_url=data.get("previewUrl"),
    )


# get artist by name
def get_artists(artist_name: str, limit: int) -> list[Artist]:
    params: dict[str, str | int] = {
        "term": artist_name,
        "entity": "musicArtist",
        "limit": limit,
    }
    res = requests.get("https://itunes.apple.com/search", params=params)
    if res.status_code == 200:
        data = res.json()
        artists = data.get("results", [])
        logger.info(f"Loaded {len(artists)} artists from iTunes")
        return [map_artist(x) for x in artists]

    else:
        logger.error(
            f"""get_artist failed on {
            artist_name}: {res.status_code}"""
        )
        return []


# get artist by album
def get_artist_by_album(album: Album) -> Artist:
    params: dict[str, str | int] = {"id": album.artist_id, "entity": "musicArtist"}
    res = requests.get("https://itunes.apple.com/lookup", params=params)
    if res.status_code == 200:
        data = res.json()
        artists = data.get("results", [])[1:]
        logger.info(
            f"""Loaded {len(artists)} artists of {
            album.artist_id} from iTunes"""
        )
        return Artist(
            album.artist_id,
            artists[0]["artistName"],
            artists[0]["artistViewUrl"],
        )
    else:
        logger.error(
            f"""get_artist_by_album failed on {
            album.artist_id}: {res.status_code}"""
        )
        return Artist(
            0,
            "",
        )


# get artist by track
def get_artist_by_track(track: Track) -> Artist:
    params: dict[str, str | int] = {"id": track.artist_id, "entity": "musicArtist"}
    res = requests.get("https://itunes.apple.com/lookup", params=params)
    if res.status_code == 200:
        data = res.json()
        artists = data.get("results", [])[1:]
        logger.info(
            f"""Loaded {len(artists)} artists of {
            track.artist_id} from iTunes"""
        )
        return Artist(
            track.artist_id,
            artists[0]["artistName"],
            artists[0]["artistViewUrl"],
        )
    else:
        logger.error(
            f"""get_artist_by_track failed on {
            track.artist_id}: {res.status_code}"""
        )
        return Artist(
            0,
            "",
        )


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


# get albums by artist
def get_albums_by_artist(artist: Artist) -> None:
    params: dict[str, str | int] = {"id": artist.id, "entity": "album"}
    res = requests.get("https://itunes.apple.com/lookup", params=params)
    if res.status_code == 200:
        data = res.json()
        albums = data.get("results", [])[1:]
        logger.info(f"Loaded {len(albums)} albums of {artist.name} from iTunes")
        artist.albums = [map_album(x) for x in albums]
    else:
        logger.error(f"get_albums_by_artist failed on {artist.name}: {res.status_code}")
        artist.albums = []


# get tracks by name
def get_tracks(track_name: str, limit: int) -> list[Track]:
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


# get tracks by album
def get_tracks_by_album(album_id) -> list[Track]:
    params: dict[str, str | int] = {"id": album_id, "entity": "song"}
    res = requests.get("https://itunes.apple.com/lookup", params=params)
    if res.status_code == 200:
        data = res.json()
        tracks = data.get("results", [])[1:]
        logger.info(f"Loaded {len(tracks)} tracks of {album_id} from iTunes")
        return [map_track(x) for x in tracks]
    else:
        logger.error(f"get_tracks_by_album failed on {album_id}: {res.status_code}")
        return []


# @cache_artist
def search_artists(artist_name: str, limit: int) -> list[Artist]:
    artist = get_artists(artist_name, limit)
    for a in artist:
        get_albums_by_artist(a)

    return artist


def search_artist_by_album(album: Album) -> Artist:
    artist = get_artist_by_album(album)
    return artist


def search_artist_by_track(track: Track) -> Artist:
    artist = get_artist_by_track(track)
    for album in artist.albums:
        get_tracks_by_album(album)
    return artist


def search_albums(album_name: str, limit: int) -> list[Album]:
    albums = get_albums(album_name, limit)
    for album in albums:
        album.tracks = get_tracks_by_album(album.id)
    return albums


def search_tracks(track_name: str, limit: int) -> list[Track]:
    return get_tracks(track_name, limit)


def search_tracks_by_album(album_id: str) -> list[Track]:
    tracks = get_tracks_by_album(album_id)
    return tracks
