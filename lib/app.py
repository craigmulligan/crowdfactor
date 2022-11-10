from flask import Flask
from lib.db import DB
from lib.graph import Graph
from lib import forecast
from lib import utils
from lib.config import Config
from flask import render_template
from datetime import datetime, timezone

app = Flask(__name__)

app.config.from_object(Config())
# Ensure the db connection is torn down..
app.teardown_appcontext(DB.tear_down)


@app.route("/")
def index():
    # get current datetime
    spot_id = app.config["SURFLINE_SPOT_ID"]
    spot_forecast = forecast.get_latest(spot_id)
    spot_info = forecast.get_spot_info(spot_id)

    window_start = utils.epoch_to_datetime(spot_forecast[0]["timestamp"])
    window_end = utils.epoch_to_datetime(spot_forecast[-1]["timestamp"])

    db = DB.get_db()
    reading = db.latest_reading(spot_id)
    if not reading:
        raise Exception(f"No readings for {spot_id} yet.")

    ts = datetime.strptime(reading["timestamp"], utils.DATETIME_FORMAT)

    # Group by hour + day of the week and surf_rating.
    # So we can predict based crowds based on the forecasted surf_rating
    predictions = db.predictions(spot_id, window_start, window_end)
    readings = db.readings(spot_id, window_start, window_end)

    graph = Graph.render(predictions, readings, spot_forecast)

    # Make sure reading is in local tz.
    reading["timestamp"] = utils.local_timestamp(ts, spot_info["utcOffset"]).strftime(
        utils.DATETIME_FORMAT
    )
    return render_template("index.html", **reading, graph=graph, spot_info=spot_info)
