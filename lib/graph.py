from typing import List, Dict
from lib.forecast import Rating
import pygal
from datetime import datetime


class Graph:
    @staticmethod
    def render(input: List[Dict], forecast: List[Rating]):
        hist = pygal.Histogram(height=300)
        hist.title = "Average crowds for FAIR surf on tuesday."
        hist.show_legend = False

        brap = []

        for f in forecast:
            h = datetime.fromtimestamp(f["timestamp"]).hour
            rating = f["rating"]["key"]

        data = []
        for i in input:
            h = int(i["hour"])
            data.append((i["avg_crowd_count"], h, h + 1))

        hist.add("Popular times for this spot", data)

        return hist.render_data_uri()
