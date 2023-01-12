
def test_index(client, spot_id, mock_surf_rating_forecast, mock_weather_forecast, mock_spot_info, pretrained_model):
    """
    Asserts the index page renders data correctly from the db.
    """
    response = client.get(f"/")
    mock_surf_rating_forecast.assert_called_once_with(spot_id)

    # make sure the graph doesn't throw.
    assert response.status_code == 200
