def test_index(client, db, seed, spot_id, mock_forecast):
    """
    Asserts the index page renders data correctly from the db.
    """
    response = client.get(f"/")
    mock_forecast.assert_called_once_with(spot_id)

    # make sure the graph doesn't throw.
    assert response.status_code == 200
