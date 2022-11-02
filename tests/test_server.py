def test_index(client, db, seed, spot_id, mock_forecast):
    """
    Asserts the index page renders data correctly from the db.
    """
    response = client.get(f"/")
    mock_forecast.assert_called_once_with(spot_id)
    latest = db.latest_reading(spot_id)

    assert response.status_code == 200
    assert latest["surf_rating"] == "GOOD"
    assert latest["crowd_count"] == 6
    assert latest["timestamp"] == "2022-10-29T23:00:00"
