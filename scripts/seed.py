from lib.db import DB
from lib.app import app

if __name__ == "__main__":
    # Running in flask app
    # context ensures we cleanup db connections
    # etc.
    with app.app_context():
        db = DB.get_db()
        # ensure db schema
        db.setup()

        # for range over the 3rd to 10th oct.
        # which is Monday-Sunday
        for d in range(3, 10):
            for h in range(24):
                # for each hour in the day.
                db.insert(
                    h,  # make crowd count equal to hour so it's easy to assert.
                    "FAIR",
                    f"2022-10-{d:02}T{h:02}:00:00",
                )
