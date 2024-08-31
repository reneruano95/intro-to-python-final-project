import logging
from model.artist import Artist
from service.itunes import iTunesAlbumService
from service.AlbumService import AlbumService
from service.filecache import FileCacheAlbumService

AlbumService.init([FileCacheAlbumService(), iTunesAlbumService()])


def test_service():
    artist = Artist("John Mayer")
    artist.get_albums(3)
    desc = str(artist)
    logging.info(desc)
    assert len(desc) > 0
