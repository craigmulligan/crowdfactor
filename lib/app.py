from flask import Flask
from lib.db import DB
from lib.graph import Graph
from lib import forecast
from lib import utils
from flask import render_template
from datetime import datetime, timezone
from os import environ

app = Flask(__name__)

# Ensure the db connection is torn down..
app.teardown_appcontext(DB.tear_down)


@app.route("/")
def index():
    # get current datetime
    spot_id = environ["SURFLINE_SPOT_ID"]
    spot_forecast = forecast.get_latest(spot_id)
    dt = datetime.now().replace(tzinfo=timezone.utc)
    weekday = dt.isoweekday()

    db = DB.get_db()
    # TODO: make sure reading is
    reading = db.latest_reading(spot_id)
    assert reading
    if reading is None:
        raise Exception(f"No readings for {spot_id} yet.")

    reading["timestamp"] = utils.local_timestamp(
        reading["timestamp"], spot_forecast[0]["utcOffset"]
    )

    # Group by hour + day of the week and surf_rating.
    # So we can predict based crowds based on the forecasted surf_rating
    predictions = db.predictions(spot_id, weekday)
    if not predictions:
        raise Exception(f"No readings for {spot_id} and weekday {weekday} yet.")

    graph = Graph.render(predictions, spot_forecast)

    return render_template("index.html", **reading, graph=graph)
