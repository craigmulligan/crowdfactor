from typing import TypedDict, List
import requests


class Condition(TypedDict):
    key: str
    value: int


class Rating(TypedDict):
    timestamp: int
    rating: Condition


def get_latest(spot_id) -> List[Rating]:
    url = f"https://services.surfline.com/kbyg/spots/forecasts/rating/{spot_id}days=1&intervalHours=1"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()["data"]["rating"]
