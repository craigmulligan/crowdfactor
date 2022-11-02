def test_index(client, db, seed, spot_id):
    """
    Asserts the index page renders data correctly from the db.
    """
    response = client.get(f"/{spot_id}")
    latest = db.latest_reading()

    assert response.status_code == 200
    assert latest["surf_rating"] == "FAIR"
    # last hour of the day so should be 23.
    assert latest["crowd_count"] == 3
    assert latest["timestamp"] == "6-23"
    assert latest["spot_id"] == spot_id
