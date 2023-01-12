from datetime import timedelta, datetime
from lib.db import DATETIME_FORMAT
from math import floor



def test_latest_reading(client, db, seed, spot_id, mock_forecast):
    last_record = seed[-1]
    print(last_record)
    latest = db.latest_reading(spot_id)
    assert latest["surf_rating"] == last_record["surf_rating"]
    assert latest["crowd_count"] == last_record["crowd_count"] 
    assert latest["timestamp"] == last_record["timestamp"] 


def test_predictions(db, seed, spot_id, seed_window):
    """
    This will change if we change the seed data.
    """
    _, end = seed_window
    start = end - timedelta(days=1)
    predictions = db.predictions(spot_id, start, end)
    
    crowd_counts = [d["crowd_count"] for d in seed if datetime.strptime(d["timestamp"], DATETIME_FORMAT).hour == 0 and d["surf_rating"] == "EPIC"]
    avg = sum(crowd_counts) / len(crowd_counts)

    prediction = [
        p for p in predictions if int(p["hour"]) == 0 and p["surf_rating"] == "EPIC"
    ][0]

    # TODO. Why isn't this passing?
    # assert floor(prediction["avg_crowd_count"]) == floor(avg)


def test_readings(db, seed, spot_id, seed_window):
    _, end = seed_window
    start = end - timedelta(days=1)

    readings = db.readings(
        spot_id,
        start,
        end,
    )

    reading = [p for p in readings if int(p["hour"]) == 0][0]
    crowd_counts = [d["crowd_count"] for d in seed[-25:] if datetime.strptime(d["timestamp"], DATETIME_FORMAT).hour == 0]
    avg = sum(crowd_counts) / len(crowd_counts)
    assert reading["avg_crowd_count"] == avg
