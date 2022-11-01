from lib.db import DB
from lib.app import app
import random
from collections import deque

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
        conditions = deque(["FAIR", "GOOD", "EPIC"])
        conditions_max = {"FAIR": 10, "GOOD": 15, "EPIC": 30}

        # Oct 3 - 30th
        # 4 weeks of data
        for d in range(3, 30):
            conditions.rotate(1)
            random.seed(d)
            r = range(0, 24)
            total_hours = len(r)
            factor = total_hours / len(conditions)
            for h in r:
                if h % factor == 0:
                    conditions.rotate(1)
                # for each hour in the day.

                crowd_count = random.randint(0, conditions_max[conditions[0]])

                db.insert(
                    crowd_count,  # make crowd count equal to hour so it's easy to assert.
                    conditions[0],
                    f"2022-10-{d:02}T{h:02}:00:00",
                )
