from abc import ABC, abstractmethod
from typing import List

from model.album import Album
from model.track import Track


class AlbumService(ABC):
    _services: List['AlbumService'] = []

    @abstractmethod
    async def get_albums(self, artist_name: str, limit: int) -> List[Album]:
        pass

    @abstractmethod
    async def get_tracks(self, album_id: int) -> List[Track]:
        pass

    @classmethod
    def init(cls, services: List['AlbumService']):
        """
        Initializes the array of album services to be used as a singleton.
        """
        if not cls._services:
            cls._services = services
        else:
            raise Exception("Services have already been initialized.")

    @classmethod
    def services(cls) -> List['AlbumService']:
        """
        Returns the singleton array of album services.
        """
        if not cls._services:
            raise Exception("Services have not been initialized yet.")
        return cls._services
