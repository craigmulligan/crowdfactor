
def test_index(client, spot_id, mock_spot_report, mock_forecasts, pretrained_model, mock_surf_rating_forecast):
    """
    Asserts the index page renders data correctly from the db.
    """
    response = client.get(f"/")
    mock_surf_rating_forecast.assert_called_once_with(spot_id)

    # make sure the graph doesn't throw.
    assert response.status_code == 200
