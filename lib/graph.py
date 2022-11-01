from typing import List, Dict
import pygal


class Graph:
    @staticmethod
    def render(input: List[Dict]):
        hist = pygal.Histogram(height=300)
        hist.title = "Average crowds for FAIR surf on tuesday."
        hist.show_legend = False

        data = []
        for i in input:
            h = int(i["hour"])
            data.append((i["avg_crowd_count"], h, h + 1))

        hist.add("Popular times for this spot", data)

        return hist.render_data_uri()
