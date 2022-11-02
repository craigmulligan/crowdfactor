from typing import Dict
from flask import Flask
from lib.db import DB
from lib.graph import Graph
from lib import forecast
from flask import render_template
from datetime import datetime, timezone


app = Flask(__name__)

# Ensure the db connection is closed.
app.teardown_appcontext(DB.tear_down)


@app.route("/<spot_id>")
def index(spot_id):
    # get current datetime
    spot_forecast = forecast.get_latest(spot_id)
    dt = datetime.now().replace(tzinfo=timezone.utc)
    weekday = dt.isoweekday()
    print("Weekday is:", weekday)

    db = DB.get_db()
    current = db.query(
        """
            select surf_rating, crowd_count, timestamp from crowd_log where spot_id = ? order by timestamp desc limit 1;
        """,
        [spot_id],
        one=True,
    )
    assert isinstance(current, Dict)

    # Group by hour + day of the week and surf_rating.
    # So we can predict based crowds based on the forecasted surf_rating
    predictions = db.query(
        f"""
            select avg(crowd_count) as avg_crowd_count, strftime('%H', timestamp) as hour, surf_rating from crowd_log where strftime('%w', timestamp) = ? and spot_id = ? group by strftime('%H', timestamp), surf_rating;
        """,
        [str(weekday), spot_id],
    )
    assert predictions
    graph = Graph.render(predictions, spot_forecast)

    return render_template("index.html", **current, graph=graph)
