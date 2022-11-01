def test_index(client, db, seed):
    """
    Asserts the index page renders data correctly from the db.
    """
    response = client.get("/")
    latest = db.latest_reading()

    assert response.status_code == 200
    assert latest["surf_rating"] == "FAIR"
    # last hour of the day so should be 23.
    assert latest["crowd_count"] == 23
