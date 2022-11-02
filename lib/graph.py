from typing import List, Optional, TypedDict
from lib.forecast import Rating
import pygal
from datetime import datetime


class CrowdPrediction(TypedDict):
    hour: str
    surf_rating: str
    avg_crowd_count: int


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
        forecast: List[Rating],
    ):
        find = prediction_finder(predictions)

        x_labels = []
        values = []

        for f in forecast:
            h = datetime.fromtimestamp(f["timestamp"]).hour
            rating = f["rating"]["key"]
            val = find(rating, h)
            if h % 2:
                x_labels.append(f"{h:02}:00")
            else:
                x_labels.append(None)

            values.append({"value": val, "color": style_map[rating], "label": rating})

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
