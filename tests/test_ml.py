from lib.ml import Model, predict, SurfRating, WeatherConditions
import pytest
from datetime import datetime, timedelta, timezone
from lib.seed import seed as seed_db
from lib.db import DATETIME_FORMAT
import os

def test_predict(spot_id, pretrained_model, mock_surf_rating_forecast, mock_weather_forecast):
    """
    Given a spot_id, spot_forecast + weather_forecast.
    predict the crowd count for each day 
    """
    weather_forecast = mock_weather_forecast(spot_id)
    rating_forecast = mock_surf_rating_forecast(spot_id)
    predictions = predict(rating_forecast, weather_forecast)

    assert len(predictions) == 24 
    first_prediction = predictions[0]
    assert isinstance(first_prediction["crowd_count_predicted"], int)


def test_train_and_persist(spot_id, db, seed, app):
    # Use all data we have on first train.
    # train on all but 1. And use random 1 to ensure it's the same randomness seed
    # on each call.
    x_train, x_test, y_train, y_test = Model.get_training_data(random_state=1)
    model = Model.load()
    model.train(x_train, y_train)
    i = [6, 29, 5, 1, 2]
    prediction = model.predict(*i)
    assert isinstance(prediction, float)
    score = model.score(x_test, y_test)
    assert isinstance(score, float)

    model.persist()
    model.log(score)

    latest_training_log = db.latest_training_log(model.get_url())
    assert latest_training_log["score"] == score
    assert os.path.isfile(model.get_url())

    # now train again.
    model = Model.load()

    # There shouldn't be anymore data.
    with pytest.raises(Exception, match="No training data"):
        x_train, x_test, y_train, y_test = Model.get_training_data(random_state=1)

    # lets add some more data random data.
    start = datetime.utcnow()
    end = start + timedelta(days=1)
    seed_db(spot_id, start, end)

    # There shouldn't be anymore data.
    x_train, x_test, y_train, y_test = Model.get_training_data(random_state=1)
    model.train(x_train, y_train)

    new_prediction = model.predict(*i)
    assert isinstance(new_prediction, float)

@pytest.mark.skipif("DB_URL" not in os.environ,
                    reason="requires DB_URL to be set")
def test_real_data():
    """
    Use this test to tweak the model and run real data.
    """

    x_train, x_test, y_train, y_test = Model.get_training_data(random_state=42)
    model = Model.load()
    model.train(x_train, y_train)
    print(y_train)

    ts = datetime.strptime("2023-01-23 15:51:40", DATETIME_FORMAT).replace(tzinfo=timezone.utc)
    weekday = ts.isoweekday()
    hour = ts.hour
    rating_value = SurfRating["FAIR"].value 
    weather_temperature = int(9.0)
    weather_condition_value = WeatherConditions["CLEAR"].value
    expected_crowd_count = 0
    
    score = model.score(x_test, y_test)
    prediction = model.predict(rating_value, weather_temperature, weather_condition_value, weekday, hour)
    
    assert abs(expected_crowd_count - prediction) < 1
