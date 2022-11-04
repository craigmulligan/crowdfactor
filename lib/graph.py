from typing import List, Optional, TypedDict
from lib.forecast import Forecast
from lib import utils
import pygal
from datetime import datetime


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


def reading_finder(input: List[CrowdCount]):
    def inner(hour: int) -> Optional[int]:
        for i in input:
            if int(i["hour"]) == hour:
                return i["avg_crowd_count"]
        return None

    return inner


style_map = {
    "FLAT": (255, 165, 0),  # incorrect orange.,
    "VERY_POOR": (255, 165, 0),  # incorrect orange.
    "POOR": (64, 143, 255),
    "POOR_TO_FAIR": (48, 210, 232),
    "FAIR": (26, 214, 76),
    "FAIR TO GOOD": (255, 205, 30),
    "GOOD": (255, 165, 0),  # incorrect orange.
    "VERY GOOD": (255, 0, 0),  # incorrect red.
    "GOOD TO EPIC": (255, 192, 203),  # incorrect pink
    "EPIC": (128, 0, 128),  # incorrect purple
}


class Graph:
    @staticmethod
    def render(
        predictions: List[CrowdPrediction],
        forecast: List[Forecast],
        readings: List[CrowdCount],
    ):
        find_prediction = prediction_finder(predictions)
        find_reading = reading_finder(readings)

        x_labels = []
        predictions_series = []
        readings_series = []

        for f in forecast:
            ts = datetime.fromtimestamp(f["timestamp"])
            rating = f["rating"]["key"]
            prediction = find_prediction(rating, ts.hour)
            reading = find_reading(ts.hour)
            offset = f["utcOffset"]
            local_ts = utils.local_timestamp(ts, offset)

            if local_ts.hour % 2:
                x_labels.append(f"{local_ts.hour:02}:00")
            else:
                x_labels.append(None)

            label = f"{rating}\n - {local_ts.strftime('%d/%m/%Y')}"

            r, g, b = style_map[rating]

            predictions_series.append(
                {
                    "value": (prediction, local_ts.hour, local_ts.hour + 1),
                    "color": f"rgba({r}, {g}, {b}, 0.5)",
                    "label": label,
                }
            )

            readings_series.append(
                {
                    "value": [reading, local_ts.hour, local_ts.hour + 1],
                    "color": f"rgba({r}, {g}, {b}, 0.5)",
                    "label": label,
                }
            )

        chart = pygal.Histogram()
        chart.show_legend = False
        chart.title = "Crowd factor for today"
        chart.height = 300

        chart.add(
            "Predicted crowd",
            predictions_series,
        )
        chart.add(
            "Predicted crowd",
            predictions_series,
        )
        chart.add("Recorded crowd", readings_series)

        return chart.render_data_uri()
