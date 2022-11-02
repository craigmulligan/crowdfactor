from lib.utils import get_spot_id


def test_spot_id(spot_id, surfline_url):
    result = get_spot_id(surfline_url)
    assert result == spot_id
