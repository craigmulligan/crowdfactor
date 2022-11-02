from typing import TypedDict, List
import requests


class Condition(TypedDict):
    key: str
    value: int


class Rating(TypedDict):
    timestamp: int
    rating: Condition


def get_latest(spot_id) -> List[Rating]:
    # Headers are needed otherwise surfline tries to bounce you.
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    url = f"https://services.surfline.com/kbyg/spots/forecasts/rating?spotId={spot_id}&days=1&intervalHours=1"
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    return res.json()["data"]["rating"]
