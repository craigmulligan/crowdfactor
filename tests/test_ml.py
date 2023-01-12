from lib.ml import Model, predict
import pytest
import os.path
from datetime import datetime, timedelta
from lib.seed import seed as seed_db
from lib.forecast import get_spot_surf_rating, get_spot_weather

def test_predict(spot_id, pretrained_model):
    """
    Given a spot_id, spot_forecast + weather_forecast.
    predict the crowd count for each day 
    """
    weather_forecast = get_spot_weather(spot_id)
    rating_forecast = get_spot_surf_rating(spot_id)
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
