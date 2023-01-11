from lib.db import DB
from lib import utils
from collections import deque
import random
from datetime import timedelta, datetime
from lib.camera import Conditions
import csv


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


def seed_training_data():
    db = DB.get_db()
    db.setup()

    with open("tests/data/training-data.csv") as f:
        reader = csv.DictReader(f)
        values = [tuple(r.values()) for r in reader]
        print(values[0])
        db.conn.executemany(
            f"""
            INSERT INTO crowd_log (timestamp,crowd_count,surf_rating,spot_id,model_version,wave_height_min,wave_height_max,weather_temp,weather_condition,water_temp_max,water_temp_min,wind_direction,wind_gust,wind_speed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
            values,
        )


def seed(spot_id, start: datetime, end: datetime):
    db = DB.get_db()
    db.setup()
    # for range over the 3rd to 10th oct.
    # which is Monday-Sunday
    conditions = deque(
        [
            "FLAT",
            "VERY_POOR",
            "POOR",
            "POOR_TO_FAIR",
            "FAIR",
            "FAIR_TO_GOOD",
            "GOOD",
            "VERY_GOOD",
            "GOOD_TO_EPIC",
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
        "FAIR_TO_GOOD": 15,
        "GOOD": 15,
        "VERY_GOOD": 20,
        "GOOD_TO_EPIC": 25,
        "EPIC": 30,
    }

    for dt in daterange(start, end):
        r = random.randint(0, len(conditions))
        conditions.rotate(r)
        random.seed(dt.timestamp())
        r = range(0, 24)
        total_hours = len(r)
        factor = total_hours / len(conditions)
        for h in r:
            if h % factor == 0:
                conditions.rotate(1)
            # for each hour in the day.

            c = Conditions(
                wind_direction=149.1,
                wind_speed=34,
                wind_gust=6,
                water_temp_max=18,
                water_temp_min=14,
                weather_temp=22,
                weather_condition="MIST",
                wave_height_max=2,
                wave_height_min=1,
                surf_rating=conditions[0],
            )
            crowd_count = random.randint(0, conditions_max[conditions[0]])

            db.insert(
                crowd_count,
                c,
                spot_id,
                dt.replace(hour=h).strftime(utils.DATETIME_FORMAT),
                2,
            )
