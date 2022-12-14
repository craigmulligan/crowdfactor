from typing import TypedDict, List
import requests
from lib.cache import shelve_it
import json


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


# TODO add an expire arg to shelve_it and cache this.
def get_latest(spot_id) -> List[Forecast]:
    url = f"https://services.surfline.com/kbyg/spots/forecasts/rating?spotId={spot_id}&days=1&intervalHours=1"
    res = requests.get(url)
    res.raise_for_status()

    return res.json()["data"]["rating"]


@shelve_it
def get_spot_info(spot_id) -> SpotInfo:
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/reports?spotId={spot_id}&corrected=false"
    )
    res.raise_for_status()
    data = res.json()

    return {
        "name": data["spot"]["name"],
        "utcOffset": data["associated"]["utcOffset"],
        "href": data["associated"]["href"],
    }
