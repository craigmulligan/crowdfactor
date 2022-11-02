from typing import Dict
from flask import Flask
from lib.db import DB
from lib.graph import Graph
from lib import forecast
from flask import render_template
from datetime import datetime, timezone


app = Flask(__name__)

# Ensure the db connection is torn down..
app.teardown_appcontext(DB.tear_down)


@app.route("/<spot_id>")
def index(spot_id):
    # get current datetime
    spot_forecast = forecast.get_latest(spot_id)
    dt = datetime.now().replace(tzinfo=timezone.utc)
    weekday = dt.isoweekday()

    db = DB.get_db()
    reading = db.latest_reading(spot_id)
    assert reading
    if reading is None:
        raise Exception(f"No readings for {spot_id} yet.")

    # Group by hour + day of the week and surf_rating.
    # So we can predict based crowds based on the forecasted surf_rating
    predictions = db.predictions(spot_id, weekday)
    if not predictions:
        raise Exception(f"No readings for {spot_id} and weekday {weekday} yet.")

    graph = Graph.render(predictions, spot_forecast)

    return render_template("index.html", **reading, graph=graph)
