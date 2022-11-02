from typing import List, Optional, TypedDict
from lib.forecast import Rating
import pygal
from datetime import datetime


class CrowdHistory(TypedDict):
    hour: str
    surf_rating: str
    avg_crowd_count: int


def historical_loader(input: List[CrowdHistory]):
    """
    Input is a the average crowd count grouped by hour + surf_rating

    This function returns the crowd_count for the hour and surf_rating supplied.
    """

    def inner(rating: str, hour: int) -> Optional[int]:
        for i in input:
            if int(i["hour"]) == hour and i["surf_rating"] == rating:
                return i["avg_crowd_count"]
        return None

    return inner


# def x_formatter(val: float):
#     return f"{int(val)} in the water"


def x_formatter(val: float):
    return f"{int(val):02}:00"


class Graph:
    @staticmethod
    def render(input: List[CrowdHistory], forecast: List[Rating]):
        loader = historical_loader(input)
        hist = pygal.Histogram(height=300)
        hist.title = "Average crowds for surf on tuesday."
        hist.show_legend = False

        conditions = {}

        for f in forecast:
            h = datetime.fromtimestamp(f["timestamp"]).hour
            rating = f["rating"]["key"]
            crowd_count = loader(rating, h)
            val = (
                {"value": crowd_count},
                {"value": h, "label": f"{int(h):02}:00"},
                {"value": h, "label": f"{int(h + 1):02}:00"},
            )
            # val = (crowd_count, h, h + 1)
            if conditions.get(rating) is None:
                conditions[rating] = [val]
            else:
                conditions[rating].append(val)

        for k, v in conditions.items():
            hist.add(k, v)

        return hist.render_data_uri()
