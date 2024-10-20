from dataclasses import dataclass, field
from typing import List
from model.track import Track


@dataclass
class Album:
    id: int
    title: str
    image_url: str
    tracks: List[Track] = field(default_factory=list)
