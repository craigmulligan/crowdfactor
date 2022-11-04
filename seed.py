from lib.db import DB
from lib.app import app
from lib.seed import seed
from datetime import datetime

if __name__ == "__main__":
    # Running in flask app
    # context ensures we cleanup db connections
    # etc.
    with app.app_context():
        db = DB.get_db()
        # ensure db schema
        db.setup()
        seed("590927576a2e4300134fbed8", datetime(2015, 12, 20), datetime(2018, 1, 11))
