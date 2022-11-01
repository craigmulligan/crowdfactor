from typing import Dict
from flask import Flask
from lib.db import DB
from flask import render_template

app = Flask(__name__)

# Ensure the db connection is closed.
app.teardown_appcontext(DB.tear_down)


@app.route("/")
def hello_world():

    db = DB.get_db("thelocal.db")
    current = db.query(
        """
            select surf_rating, crowd_count, timestamp from crowd_log order by timestamp desc limit 1;
        """,
        one=True,
    )
    assert isinstance(current, Dict)

    return render_template("index.html", **current)
