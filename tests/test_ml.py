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
    model = Model.load()
    x_train, x_test, y_train, y_test = model.get_training_data(random_state=1)
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
        x_train, x_test, y_train, y_test = model.get_training_data(random_state=1)

    # lets add some more data random data.
    start = datetime.utcnow()
    end = start + timedelta(days=1)
    seed_db(spot_id, start, end)

    # There shouldn't be anymore data.
    x_train, x_test, y_train, y_test = model.get_training_data(random_state=1)
    model.train(x_train, y_train)

    new_prediction = model.predict(*i)
    assert isinstance(new_prediction, float)

@pytest.mark.skipif("DB_URL" not in os.environ,
                    reason="requires DB_URL to be set")
def test_real_data():
    """
    Use this test to tweak the model and run real data.
    """
    model = Model.load()
    x_train, x_test, y_train, y_test = model.get_training_data(random_state=42)
    model.train(x_train, y_train)

    train_score = model.score(x_train, y_train)
    # Best possible score is 1.
    assert 0 < train_score < 1.5
    print("training score", train_score)


    test_score = model.score(x_test, y_test)
    # Best possible score is 1.
    assert 0 < test_score < 1.5
    print(f"training score: {train_score}, test score: {test_score}")

    examples = [
        ("2023-01-23 15:51:40", "FAIR", 9, "CLEAR", 0)
    ]

    for e in examples:
        print("predicting...")
        ts, surf_rating, weather_temperature, weather_condition, expected_crowd_count = e 
        dt = datetime.strptime(ts, DATETIME_FORMAT).replace(tzinfo=timezone.utc)
        weekday = dt.isoweekday()
        hour = dt.hour
        rating_value = SurfRating[surf_rating].value 
        weather_condition_value = WeatherConditions[weather_condition].value
        
        prediction = model.predict(rating_value, weather_temperature, weather_condition_value, weekday, hour)
        print(f"prediction: {prediction} expected: {expected_crowd_count}") 

    assert False
