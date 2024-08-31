def format_millis(millis: int) -> str:
    secs = millis/1000
    mins = secs/60
    return f"{mins:.0f}:{secs % 60:02.0f}"


class Track:
    def __init__(self, name: str, disc: int, number: int, time_millis: int, preview_url: str):
        self.name = name
        self.disc = disc
        self.number = number
        self.time_millis = time_millis
        self.preview_url = preview_url

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "disc": self.disc,
            "number": self.number,
            "time_millis": self.time_millis,
            "preview_url": self.preview_url
        }

    def __str__(self) -> str:
        return f"   {self.disc}-{self.number}: {self.name} [{format_millis(self.time_millis)}]"
