from dataclasses import asdict, dataclass, field
import json
from typing import List
from model.album import Album
from service.AlbumService import AlbumService
from service.filecache import cache_albums


@dataclass
class Artist:
    name: str
    albums: List[Album] = field(default_factory=list)

    async def get_albums(self, limit: int) -> None:
        """Iterates through the configured album services to 
        get albums for the artist, effectively caching the results of
        albums that have been downloaded.

        Args:
            limit (int): number of albums to get
        """
        for service in AlbumService.services():
            try:
                self.albums = await service.get_albums(self.name, limit)
                for album in self.albums:
                    tracks = await service.get_tracks(album.id)
                    if tracks:
                        album.tracks = tracks
                break
            except:
                continue

        # cache results
        cache_albums(self.name, self.albums)

    def __str__(self):
        return json.dumps(asdict(self), indent=2)
