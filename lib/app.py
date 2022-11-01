from typing import Dict
from flask import Flask
from lib.db import DB
from flask import render_template
from datetime import datetime


app = Flask(__name__)

# Ensure the db connection is closed.
app.teardown_appcontext(DB.tear_down)


@app.route("/")
def hello_world():
    # get current datetime
    dt = datetime.now()
    weekday = dt.isoweekday()

    print("Weekday is:", weekday)

    db = DB.get_db()
    current = db.query(
        """
            select surf_rating, crowd_count, strftime('%w-%H', timestamp) as timestamp from crowd_log order by timestamp desc limit 1;
        """,
        one=True,
    )
    print(current)
    assert isinstance(current, Dict)

    return render_template("index.html", **current)
