from lib.db import DB
from lib import utils
from collections import deque
import random
from datetime import timedelta, datetime


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


def seed(spot_id):
    db = DB.get_db()
    db.setup()
    # for range over the 3rd to 10th oct.
    # which is Monday-Sunday
    conditions = deque(
        [
            "FLAT",
            "VERY POOR",
            "POOR",
            "POOR TO FAIR",
            "FAIR",
            "FAIR TO GOOD",
            "GOOD",
            "VERY_GOOD",
            "GOOD TO EPIC",
            "EPIC",
        ]
    )
    # 1 = FLAT: Unsurfable or flat conditions. No surf.
    # 2 = VERY POOR: Due to lack of surf, very poor wave shape for surfing, bad surf due to other conditions like wind, tides, or very stormy surf.
    # 3 = POOR: Poor surf with some (30%) FAIR waves to ride.
    # 4 = POOR to FAIR: Generally poor surf many (50%) FAIR waves to ride.
    # 5 = FAIR: Very average surf with most (70%) waves rideable.
    # 6 = FAIR to GOOD: Fair surf with some (30%) GOOD waves.
    # 7 = GOOD: Generally fair surf with many (50%) GOOD waves.
    # 8 = VERY GOOD: Generally good surf with most (70%) GOOD waves.
    # 9 = GOOD to EPIC: Very good surf with many (50%) EPIC waves.
    # 10 = EPIC: Incredible surf with most (70%) waves being EPIC to ride and generally some of the best surf all year.
    conditions_max = {
        "FLAT": 1,
        "VERY_POOR": 3,
        "POOR": 5,
        "POOR_TO_FAIR": 7,
        "FAIR": 10,
        "FAIR TO GOOD": 15,
        "GOOD": 15,
        "VERY GOOD": 20,
        "GOOD TO EPIC": 25,
        "EPIC": 30,
    }

    start_dt = datetime(2015, 12, 20)
    end_dt = datetime(2016, 1, 11)

    for dt in daterange(start_dt, end_dt):
        conditions.rotate(1)
        random.seed(dt.timestamp())
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
                spot_id,
                dt.replace(hour=h).strftime(utils.DATETIME_FORMAT),
                2,
            )
