from lib.ml import Model 
import pytest
import os.path
from datetime import datetime, timedelta
from lib.seed import seed as seed_db

def test_train_and_persist(spot_id, db, seed, app):
    # Use all data we have on first train.
    # train on all but 1. And use random 1 to ensure it's the same randomness seed 
    # on each call.
    MAX_CROWD_COUNT = 30
    x_train, x_test, y_train, y_test = Model.get_training_data(random_state=1)
    model = Model.load()
    model.train(x_train, y_train)

    input = [ 3, 14, 14]
    prediction = model.predict([input])
    assert 0 < prediction < MAX_CROWD_COUNT 
    score = model.score(x_test, y_test)
    assert -8 < score < 8
    
    model.persist()
    model.log(score)

    latest_training_log = db.latest_training_log(model.get_url())
    assert latest_training_log["score"] == score
    assert os.path.isfile(model.get_url())
    
    # now train again.
    model = Model.load()

    # There shouldn't be anymore data.
    with pytest.raises(Exception, match='No training data'):
        x_train, x_test, y_train, y_test = Model.get_training_data(random_state=1)

    # lets add some more data random data.
    start = datetime.utcnow() 
    end = start + timedelta(days=1)
    seed_db(spot_id, start, end)

    # There shouldn't be anymore data.
    x_train, x_test, y_train, y_test = Model.get_training_data(random_state=1)
    model.train(x_train, y_train)

    new_prediction = model.predict([input])
    assert 0 < new_prediction < MAX_CROWD_COUNT 
