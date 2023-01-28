from typing import TypedDict, List, Dict
import requests
from lib.cache import cache

DEFAULT_INTERVAL = 60 * 60 * 3 # 3 hours.

class Rating(TypedDict):
    key: str
    value: int


class Forecast(TypedDict):
    timestamp: int
    rating: Rating
    utcOffset: int


class SpotInfo(TypedDict):
    name: int
    utcOffset: int
    href: str

@cache.cached(timeout=DEFAULT_INTERVAL, key_prefix='weather')
def get_spot_weather(spot_id) -> SpotInfo:
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/forecasts/weather?spotId={spot_id}&days=1&intervalHours=1"
    )
    res.raise_for_status()
    return res.json()["data"]["weather"]


@cache.cached(timeout=DEFAULT_INTERVAL, key_prefix='tides')
def get_spot_tides(spot_id) -> SpotInfo:
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/forecasts/tides?spotId={spot_id}&days=1&intervalHours=1"
    )
    res.raise_for_status()
    return res.json()["data"]["tides"]

@cache.cached(timeout=DEFAULT_INTERVAL, key_prefix='wave')
def get_spot_wave(spot_id) -> List[Dict]:
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/forecasts/wave?spotId={spot_id}&days=1&intervalHours=1"
    )
    res.raise_for_status()
    return res.json()["data"]["wave"]


@cache.cached(timeout=DEFAULT_INTERVAL, key_prefix='wind')
def get_spot_wind(spot_id) -> List[Dict]:
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/forecasts/wind?spotId={spot_id}&days=1&intervalHours=1"
    )
    res.raise_for_status()
    return res.json()["data"]["wind"]

@cache.cached(timeout=DEFAULT_INTERVAL, key_prefix='rating')
def get_spot_surf_rating(spot_id) -> List[Forecast]:
    url = f"https://services.surfline.com/kbyg/spots/forecasts/rating?spotId={spot_id}&days=1&intervalHours=1"
    res = requests.get(url)
    res.raise_for_status()

    return res.json()["data"]["rating"]


# only cache this for 1 mins
# this is used by the worker so we want it always up to date.
@cache.cached(timeout=DEFAULT_INTERVAL, key_prefix="report")
def get_spot_report(spot_id):
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/reports?spotId={spot_id}&corrected=false"
    )
    res.raise_for_status()
    return res.json()

def get_spot_info(spot_id) -> SpotInfo:
    data = get_spot_report(spot_id) 

    return {
        "name": data["spot"]["name"],
        "utcOffset": data["associated"]["utcOffset"],
        "href": data["associated"]["href"],
    }
