from flask import Flask
from lib.db import DB
from lib.graph import Graph
from lib import forecast
from lib import utils
from lib.config import Config
from lib import ml
from flask import render_template
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.config.from_object(Config())
# Ensure the db connection is torn down..
app.teardown_appcontext(DB.tear_down)


@app.route("/")
def index():
    # get current datetime
    spot_id = app.config["SURFLINE_SPOT_ID"]
    surf_rating_forecast = forecast.get_spot_surf_rating(spot_id)
    weather_forecast = forecast.get_spot_weather(spot_id)
    spot_info = forecast.get_spot_info(spot_id)
    wind_forecast = forecast.get_spot_wind(spot_id)
    wave_forecast = forecast.get_spot_wave(spot_id)
    tides_forecast = forecast.get_spot_tides(spot_id)
    spot_report = forecast.get_spot_report(spot_id)
    spot_info = forecast.get_spot_info(spot_id)


    window_start = utils.epoch_to_datetime(surf_rating_forecast[0]["timestamp"])
    window_end = utils.epoch_to_datetime(surf_rating_forecast[-1]["timestamp"])

    db = DB.get_db()
    reading = db.latest_reading(spot_id)
    if not reading:
        raise Exception(f"No readings for {spot_id} yet.")

    ts = datetime.strptime(reading["timestamp"], utils.DATETIME_FORMAT)

    # Group by hour + day of the week and surf_rating.
    # So we can predict based crowds based on the forecasted surf_rating
    # TODO: Need to replace this with the ML model predictions.
    # For each hour we need all the attributes.
    # TODO should the prediction take spot_id?
    predictions = ml.predict(spot_report, surf_rating_forecast, weather_forecast, tides_forecast, wave_forecast, wind_forecast)

    readings = db.readings(spot_id, window_start, window_end)

    graph = Graph.render(predictions, readings)

    # Make sure reading is in local tz.
    reading["timestamp"] = utils.local_timestamp(ts, spot_info["utcOffset"]).strftime(
        utils.DATETIME_FORMAT
    )
    return render_template("index.html", **reading, graph=graph, spot_info=spot_info)
