from dataclasses import dataclass


@dataclass
class Track:
    id: int
    name: str
    artist_id: int
    album_id: int
    disc: int
    number: int
    time_millis: int
    preview_url: str | None = None
