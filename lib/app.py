from typing import Dict
from flask import Flask
from lib.db import DB
from lib.graph import Graph
from flask import render_template
from datetime import datetime


app = Flask(__name__)

# Ensure the db connection is closed.
app.teardown_appcontext(DB.tear_down)


@app.route("/<spot_id>")
def index(spot_id):
    # get current datetime
    dt = datetime.now()
    weekday = dt.isoweekday()

    print("Weekday is:", weekday)

    db = DB.get_db()
    current = db.query(
        """
            select surf_rating, crowd_count, strftime('%w-%H', timestamp) as timestamp from crowd_log where spot_id = ? order by timestamp desc limit 1;
        """,
        [spot_id],
        one=True,
    )
    assert isinstance(current, Dict)

    # Group by hour + day of the week.
    data = db.query(
        f"""
            select avg(crowd_count) as avg_crowd_count, strftime('%H', timestamp) as hour, surf_rating from crowd_log where strftime('%w', timestamp) = ? and spot_id = ? group by strftime('%H', timestamp), surf_rating;
        """,
        [str(weekday), spot_id],
    )
    assert data

    graph = Graph.render(data)

    return render_template("index.html", **current, graph=graph)
