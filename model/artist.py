import json
from dataclasses import asdict, dataclass, field
from typing import List
from model.album import Album


@dataclass
class Artist:
    id: int
    name: str
    artist_view_url: str
    albums: List[Album] = field(default_factory=list)

    def __str__(self):
        return json.dumps(asdict(self), indent=2)
