from dataclasses import dataclass, field
from typing import List
from model.track import Track


@dataclass
class Album:
    id: int
    artist_id: int
    artist_name: str
    title: str
    release_date: str
    image_url: str
    genre: str
    tracks: List[Track] = field(default_factory=list)
