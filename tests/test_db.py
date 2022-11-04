def test_latest_reading(client, db, seed, spot_id, mock_forecast):
    latest = db.latest_reading(spot_id)
    assert latest["surf_rating"] == "FAIR_TO_GOOD"
    assert latest["crowd_count"] == 5
    assert latest["timestamp"] == "2021-12-31 23:00:00"


def test_predictions(client, db, seed, spot_id):
    """
    This will change if we change the seed data.
    """
    predictions = db.predictions(spot_id, 2)

    prediction = [
        p for p in predictions if int(p["hour"]) == 0 and p["surf_rating"] == "EPIC"
    ][0]

    assert prediction["avg_crowd_count"] == 14


def test_readings(client, db, seed, spot_id, seed_window):

    _, end = seed_window
    readings = db.readings(spot_id, end)

    print(readings)
    reading = [p for p in readings if int(p["hour"]) == 0][0]

    assert reading["avg_crowd_count"] == 6
