import requests


def get_latest(spot_id):
    url = f"https://services.surfline.com/kbyg/spots/forecasts/rating/{spot_id}days=1&intervalHours=1"
    res = requests.get(url)
    res.raise_for_status()
    return res.json()
