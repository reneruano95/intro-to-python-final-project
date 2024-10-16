from typing import List
from model.album import Album
from service.AlbumService import AlbumService
from service.filecache import cache_albums


class Artist:
    def __init__(self, name: str):
        self.name = name
        self.albums: List[Album] = []

    async def get_albums(self, limit: int) -> None:
        # tries services in order
        for service in AlbumService.services():
            try:
                self.albums = await service.get_albums(self.name, limit)
                for album in self.albums:
                    tracks = await service.get_tracks(album.id)
                    if tracks:
                        album.set_tracks(tracks)
                break
            except:
                continue

        # cache results
        cache_albums(self.name, self.albums)

    def __str__(self) -> str:
        albums = "\n".join([f"Album: {album}" for album in self.albums])
        return f"""
Artist:, {self.name})
------------------------------
{albums}
"""
