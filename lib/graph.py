from typing import List, Optional, TypedDict
import pygal
from datetime import datetime
from pygal.style import CleanStyle


class CrowdCount(TypedDict):
    hour: str
    avg_crowd_count: float


class CrowdPrediction(TypedDict):
    timestamp_utc: datetime
    timestamp_local: datetime
    surf_rating: str
    crowd_count_predicted: float


def reading_finder(input: List[CrowdCount]):
    def inner(hour: int) -> Optional[float]:
        for i in input:
            if int(i["hour"]) == hour:
                return round(i["avg_crowd_count"])

        return None

    return inner


style_map = {
    # Not sure they use the ones where I couldn't find the colors.
    "FLAT": (0, 0, 0),  # incorrect black.
    "VERY_POOR": (128, 128, 128),  # incorrect grey.
    "POOR": (64, 143, 255),
    "POOR_TO_FAIR": (48, 210, 232),
    "FAIR": (26, 214, 76),
    "FAIR_TO_GOOD": (255, 205, 30),
    "GOOD": (255, 137, 0),
    "VERY_GOOD": (255, 137, 0),  # incorrect (same as very good)
    "GOOD_TO_EPIC": (255, 137, 0),  # incorrect (same as good)
    "EPIC": (213, 69, 48),
}


class Graph:
    @staticmethod
    def render(
        predictions: List[CrowdPrediction],
        readings: List[CrowdCount],
    ):
        find_reading = reading_finder(readings)

        x_labels = []
        predictions_series = []
        readings_series = []
        forecast_series = []
        values = []

        for f in predictions:
            ts = f["timestamp_utc"]
            rating = f["surf_rating"]
            local_ts = f["timestamp_local"]
            prediction = f["crowd_count_predicted"]
            reading = find_reading(ts.hour)

            if reading:
                values.append(reading)

            if prediction:
                values.append(prediction)

            x_labels.append({"value": local_ts.hour, "label": f"{local_ts.hour:02}:00"})

            r, g, b = style_map[rating]

            forecast_series.append(
                {
                    "value": (None, local_ts.hour, local_ts.hour + 1),
                    "style": f"fill: rgba({r}, {g}, {b}, 0.3); stroke: none;",
                    "label": f"conditions: {rating}",
                }
            )

            predictions_series.append(
                {
                    "value": (prediction, local_ts.hour, local_ts.hour + 1),
                    "style": f"stroke-dasharray: 5, 10; stroke: rgba({r}, {g}, {b}); fill: rgba({r}, {g}, {b}, 0.3);",
                    "label": f"conditions: {rating}, crowd: {prediction}",
                }
            )

            readings_series.append(
                {
                    "value": [reading, local_ts.hour, local_ts.hour + 1],
                    "color": f"rgba({r}, {g}, {b}, 0.8)",
                    "label": f"conditions: {rating}, crowd: {reading}",
                }
            )

        if values:
            max_value = max(values)
        else:
            max_value = 1

        for f in forecast_series:
            # Make all the forecast values takeup the whole
            # Histogram
            _, start, end = f["value"]
            f["value"] = (max_value, start, end)

        chart = pygal.Histogram(
            force_uri_protocol="https",
            x_labels_major_every=2,
            show_minor_x_labels=False,
            truncate_label=5,
            style=CleanStyle,
        )

        chart.x_value_formatter = lambda x: "%.2f" % x
        chart.show_legend = False
        chart.title = "Crowd factor for today"
        chart.height = 300
        chart.x_labels = x_labels

        chart.add(
            "Forecast",
            forecast_series,
            formatter=lambda _: "",
        )
        chart.add(
            "Predicted crowd",
            predictions_series,
            formatter=lambda _: "",
            stroke_style={"width": 5, "dasharray": "3, 6, 12, 24"},
        )
        chart.add("Recorded crowd", readings_series, formatter=lambda _: "")

        return chart.render_data_uri()
