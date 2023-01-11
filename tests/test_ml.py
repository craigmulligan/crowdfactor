from lib.ml import Model 

def test_first_train(db, seed_training_data):
    # Use all data we have on first train.
    # train on all but 1. And use random 1 to ensure it's the same randomness seed 
    # on each call. 
    x_train, x_test, y_train, y_test = Model.get_training_data(random_state=1)
    model = Model.load("test-model")
    model.train(x_train, y_train)
    assert model.score(x_test, y_test) == -7.166666666666654
