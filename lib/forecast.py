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

def get_spot_weather(spot_id) -> SpotInfo:
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/forecasts/weather?spotId={spot_id}&days=1&intervalHours=1"
    )
    res.raise_for_status()
    return res.json()["data"]["weather"]


def get_spot_surf_rating(spot_id) -> List[Forecast]:
    url = f"https://services.surfline.com/kbyg/spots/forecasts/rating?spotId={spot_id}&days=1&intervalHours=1"
    res = requests.get(url)
    res.raise_for_status()

    return res.json()["data"]["rating"]

# TODO add an expire arg to shelve_it and cache this.
@shelve_it
def get_spot_info(spot_id) -> SpotInfo:
    data = get_spot_report(spot_id) 

    return {
        "name": data["spot"]["name"],
        "utcOffset": data["associated"]["utcOffset"],
        "href": data["associated"]["href"],
    }


def get_spot_report(spot_id):
    res = requests.get(
        f"https://services.surfline.com/kbyg/spots/reports?spotId={spot_id}&corrected=false"
    )
    res.raise_for_status()
    return res.json()
