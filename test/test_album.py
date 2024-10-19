import pytest
from model.track import Track
from model.album import Album


@pytest.fixture
def album_with_tracks():
    # Create track instances
    track1 = Track(name="Track 1", disc=1, number=1,
                   time_millis=300000, preview_url="http://example.com/track1")
    track2 = Track(name="Track 2", disc=1, number=2,
                   time_millis=240000, preview_url="http://example.com/track2")

    # Create an album instance and set tracks
    album = Album(id=1, title="Test Album",
                  image_url="http://example.com/album.jpg")
    album.tracks = [track1, track2]

    return album


@pytest.fixture
def empty_album():
    # Create an album instance with no tracks
    return Album(id=1, title="Empty Album", image_url="http://example.com/empty_album.jpg")


def test_set_tracks(album_with_tracks):
    # Test the set_tracks method
    album = album_with_tracks
    assert len(album.tracks) == 2
    assert album.tracks[0].name == "Track 1"
    assert album.tracks[1].name == "Track 2"


def test_to_dict(album_with_tracks):
    # Test the to_dict method
    album = album_with_tracks
    album_dict = album.to_dict()

    assert album_dict['id'] == 1
    assert album_dict['title'] == "Test Album"
    assert album_dict['image_url'] == "http://example.com/album.jpg"
    assert len(album_dict['tracks']) == 2
    assert album_dict['tracks'][0]['name'] == "Track 1"
    assert album_dict['tracks'][1]['preview_url'] == "http://example.com/track2"


def test_str(album_with_tracks):
    # Test the __str__ method
    album = album_with_tracks
    album_str = str(album)

    assert "Test Album" in album_str
    assert "http://example.com/album.jpg" in album_str
    assert "Track 1" in album_str
    assert "Track 2" in album_str


def test_empty_tracks_to_dict(empty_album):
    # Test the to_dict method with an empty tracks list
    album = empty_album
    album_dict = album.to_dict()

    assert album_dict['id'] == 1
    assert album_dict['title'] == "Empty Album"
    assert album_dict['image_url'] == "http://example.com/empty_album.jpg"
    assert album_dict['tracks'] == []  # Ensure tracks is an empty list
