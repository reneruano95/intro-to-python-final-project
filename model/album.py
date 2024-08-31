from typing import Any, List
from model.track import Track


class Album:
    def __init__(self, id: int, title: str, image_url: str):
        self.id = id
        self.title = title
        self.image_url = image_url
        self.tracks: List[Track] = []

    def set_tracks(self, tracks: List[Track]) -> None:
        self.tracks = tracks

    def to_dict(self) -> dict[str, Any]:
        tracks = [track.to_dict()
                  for track in self.tracks] if self.tracks else []
        return {
            "id": self.id,
            "title": self.title,
            "image_url": self.image_url,
            "tracks": tracks
        }

    def __str__(self) -> str:
        tracks = "\n".join([f"{track}" for track in self.tracks])
        return f"""{self.title}
{self.image_url}
{tracks}
"""
