import pytest
import service.itunes as itunes


@pytest.mark.asyncio
async def test_service():
    artist = await itunes.search_artist("The Beatles", 3)
    desc = str(artist)
    # logging.info(artist)
    assert len(desc) > 0
