from lib.db import DB
from lib.app import app
from lib.seed import seed
from lib import ml
from datetime import datetime, timedelta

if __name__ == "__main__":
    """
    This is useful for development.
    It seeds the db with data and trains the
    prediction model.
    """
    # Running in flask app
    # context ensures we cleanup db connections
    # etc.
    with app.app_context():
        spot_id = "590927576a2e4300134fbed8"
        db = DB.get_db()
        # ensure db schema
        db.setup()
        end = datetime.utcnow()
        start = end - timedelta(days=1)

        rows = seed(spot_id, start, end)
        logs = db.logs(spot_id)
        ml.train()
