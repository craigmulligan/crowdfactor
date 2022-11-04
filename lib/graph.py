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


def get_max(input: List[CrowdPrediction]):
    values = [v["avg_crowd_count"] for v in input]
    return max(values)


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
        forecast_series = []
        values = []

        for f in forecast:
            ts = datetime.fromtimestamp(f["timestamp"])
            rating = f["rating"]["key"]
            prediction = find_prediction(rating, ts.hour)
            reading = find_reading(ts.hour)
            offset = f["utcOffset"]
            local_ts = utils.local_timestamp(ts, offset)

            if reading:
                values.append(reading)

            if prediction:
                values.append(prediction)

            if local_ts.hour % 2:
                x_labels.append(f"{local_ts.hour:02}:00")
            else:
                x_labels.append(None)

            label = f"{rating}\n - {local_ts.strftime('%d/%m/%Y')}"

            r, g, b = style_map[rating]

            forecast_series.append(
                {
                    "value": (None, local_ts.hour, local_ts.hour + 1),
                    "style": f"fill: rgba({r}, {g}, {b}, 0.3); stroke: none;",
                    "label": label,
                }
            )

            predictions_series.append(
                {
                    "value": (prediction, local_ts.hour, local_ts.hour + 1),
                    "style": f"stroke-dasharray: 5, 10; stroke: rgba({r}, {g}, {b}); fill: rgba({r}, {g}, {b}, 0.2);",
                    "label": rating,
                }
            )

            readings_series.append(
                {
                    "value": [reading, local_ts.hour, local_ts.hour + 1],
                    "color": f"rgba({r}, {g}, {b}, 1)",
                    "label": rating,
                }
            )

        max_value = max(values)

        for f in forecast_series:
            # Make all the forecast values takeup the whole
            # Histogram
            _, start, end = f["value"]
            f["value"] = (max_value, start, end)

        chart = pygal.Histogram()
        chart.show_legend = False
        chart.title = "Crowd factor for today"
        chart.height = 300

        chart.add("Forecast", forecast_series, stroke=False)
        chart.add(
            "Predicted crowd",
            predictions_series,
            stroke_style={"width": 5, "dasharray": "3, 6, 12, 24"},
        )
        chart.add(
            "Predicted crowd",
            predictions_series,
        )

        chart.add("Recorded crowd", readings_series)

        return chart.render_data_uri()
