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
    genre: str
    time_millis: int
    preview_url: str | None = None

    def formatted_time(self) -> str:
        minutes, seconds = divmod(self.time_millis // 1000, 60)
        return f"{minutes}:{seconds:02d}"