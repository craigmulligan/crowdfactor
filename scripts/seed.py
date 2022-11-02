from lib.db import DB
from lib.app import app
from lib.seed import seed

if __name__ == "__main__":
    # Running in flask app
    # context ensures we cleanup db connections
    # etc.
    with app.app_context():
        db = DB.get_db()
        # ensure db schema
        db.setup()
        seed("1234")
