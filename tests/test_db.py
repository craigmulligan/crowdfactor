from datetime import timedelta


def test_latest_reading(client, db, seed, spot_id, mock_forecast):
    latest = db.latest_reading(spot_id)
    assert latest["surf_rating"] == "FAIR_TO_GOOD"
    assert latest["crowd_count"] == 2
    assert latest["timestamp"] == "2021-12-31 23:00:00"


def test_predictions(db, seed, spot_id, seed_window):
    """
    This will change if we change the seed data.
    """
    _, end = seed_window
    start = end - timedelta(days=1)

    predictions = db.predictions(spot_id, start, end)

    prediction = [
        p for p in predictions if int(p["hour"]) == 0 and p["surf_rating"] == "EPIC"
    ][0]

    assert round(prediction["avg_crowd_count"], 2) == 17.2


def test_readings(db, seed, spot_id, seed_window):
    _, end = seed_window
    start = end - timedelta(days=7)

    readings = db.readings(
        spot_id,
        start,
        end,
    )

    reading = [p for p in readings if int(p["hour"]) == 0][0]

    assert reading["avg_crowd_count"] == 4.0 
