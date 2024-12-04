from dataclasses import dataclass


@dataclass
class Track:
    id: int
    name: str
    artist_id: int
    artist_name: str
    album_id: int
    album_name: str
    disc: int
    number: int
    release_date: str
    genre: str
    time_millis: int
    preview_url: str | None = None
