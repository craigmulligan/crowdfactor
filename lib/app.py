from flask import Flask
from lib.db import DB
from lib.graph import Graph
from lib import forecast
from lib import utils
from lib.config import Config
from lib import ml
from lib.cache import cache
from flask import render_template
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.config.from_object(Config())
# Ensure the db connection is torn down..
app.teardown_appcontext(DB.tear_down)
cache.init_app(app)


@app.route("/")
def index():
    # get current datetime
    spot_id = app.config["SURFLINE_SPOT_ID"]
    
    # TODO we should probs run this is parrellel.
    # but they do come from a cache.
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
    last_reading = db.latest_reading(spot_id)
    if not last_reading:
        raise Exception(f"No readings for {spot_id} yet.")
    
    last_training = db.latest_training_log(ml.Model.get_url())

    predictions = ml.predict(spot_report, surf_rating_forecast, weather_forecast, tides_forecast, wave_forecast, wind_forecast)
    readings = db.readings(spot_id, window_start, window_end)

    graph = Graph.render(predictions, readings)

    # Make sure last_reading + last_training is in spots local tz.
    last_reading["timestamp"] =  utils.str_to_local_timestamp(last_reading["timestamp"], spot_info["utcOffset"])

    if last_training:
        last_training["timestamp"] = utils.str_to_local_timestamp(last_training["timestamp"], spot_info["utcOffset"])

    return render_template("index.html", last_reading=last_reading, graph=graph, spot_info=spot_info, last_training=last_training)
