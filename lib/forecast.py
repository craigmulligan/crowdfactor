from typing import TypedDict, List
import requests


class Rating(TypedDict):
    key: str
    value: int


class Forecast(TypedDict):
    timestamp: int
    rating: Rating
    utcOffset: int


def get_latest(spot_id) -> List[Forecast]:
    url = f"https://services.surfline.com/kbyg/spots/forecasts/rating?spotId={spot_id}&days=1&intervalHours=1"
    res = requests.get(url)
    res.raise_for_status()

    return res.json()["data"]["rating"]
