from typing import List, Optional, TypedDict
from lib.forecast import Forecast
from lib import utils
import pygal
from datetime import datetime, timedelta, timezone


class CrowdCount(TypedDict):
    hour: str
    avg_crowd_count: int


class CrowdPrediction(CrowdCount):
    surf_rating: str


def prediction_finder(input: List[CrowdPrediction]):
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


style_map = {
    "FLAT": "",
    "VERY_POOR": "",
    "POOR": "#408fff",
    "POOR_TO_FAIR": "#30d2e8",
    "FAIR": "#1ad64c",
    "FAIR TO GOOD": "#ffcd1e",
    "GOOD": "orange",
    "VERY GOOD": "red",
    "GOOD TO EPIC": "pink",
    "EPIC": "purple",
}


class Graph:
    @staticmethod
    def render(
        predictions: List[CrowdPrediction],
        forecast: List[Forecast],
        readings: List[CrowdCount],
    ):
        find = prediction_finder(predictions)

        x_labels = []
        values = []

        for f in forecast:
            ts = datetime.fromtimestamp(f["timestamp"])
            rating = f["rating"]["key"]
            val = find(rating, ts.hour)
            offset = f["utcOffset"]

            local_ts = utils.local_timestamp(ts, offset)

            if local_ts.hour % 2:
                x_labels.append(f"{local_ts.hour:02}:00")
            else:
                x_labels.append(None)

            label = f"""
            {rating} - {local_ts.strftime('%d/%m/%Y')}
            """
            values.append({"value": val, "color": style_map[rating], "label": label})

        chart = pygal.Bar(
            height=300,
            x_labels=x_labels,
            truncate_label=-1,
            spacing=-1,
        )

        chart.title = "Average crowd predictions for today"
        chart.show_legend = False
        chart.x_labels = x_labels
        chart.add("crowd factor", values)

        return chart.render_data_uri()
