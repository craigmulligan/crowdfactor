from enum import Enum
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from lib.db import DB
from datetime import datetime
from flask import current_app
import pickle

SurfRating = Enum(
    "SurfRating",
    [
        "FLAT",
        "VERY_POOR",
        "POOR",
        "POOR_TO_FAIR",
        "FAIR",
        "FAIR_TO_GOOD",
        "GOOD",
        "VERY_GOOD",
        "GOOD_TO_EPIC",
        "EPIC",
    ],
)

class Model:
    """
    A model that can be incrementally retrained.
    see: https://datascience.stackexchange.com/questions/68599/incremental-learning-with-sklearn-warm-start-partial-fit-fit
    """
    def __init__(self) -> None:
        self.m = LinearRegression()

    @staticmethod
    def get_training_data(test_size=None, random_state=None):
        SURFLINE_SPOT_ID = current_app.config.get("SURFLINE_SPOT_ID")

        db = DB.get_db()
        logs = db.logs(SURFLINE_SPOT_ID)

        if not logs:
            raise Exception("No training data")

        labels = ["surf_rating", "weather_temp", "wind_speed"]
        feature = "crowd_count"

        x_data = []
        y_data = []

        for log in logs:
            x = []
            y = 0 

            for key, value in log.items():
                if key in labels:
                    if key == "surf_rating":
                       x.append(SurfRating[value].value) 
                    else:
                       x.append(value)
                if key == feature:
                    y = value

            x_data.append(x)
            y_data.append(y) 

        X = np.array(x_data)
        Y = np.array(y_data)

        return  train_test_split(
         X, Y, test_size=test_size, random_state=random_state,
        )
        
    @staticmethod
    def load():
        """
        We might change it to read the old model if we need to do 
        incremental learning at some point.
        """
        return Model()

    def log(self, score: float):
        """
        Logs a training event.
        """
        db = DB.get_db()
        dt = datetime.utcnow()
        db.insert_training_log(dt, score, current_app.config["MODEL_URL"])

    def persist(self):
        """
        Saves the model to disk.
        """ 
        with open(current_app.config["MODEL_URL"], 'wb') as f:
            pickle.dump(self.m, f)

    def train(self, x_train, y_train):
        self.m.fit(x_train, y_train)

    def predict(self, x_data):
        prediction = self.m.predict(x_data)
        try:
            iterator = iter(prediction) # type: ignore
        except TypeError:
            return prediction 
        else:
            return next(iterator) 


    def score(self, x_test, y_test) -> float:
        score = self.m.score(x_test, y_test)
        try:
            iterator = iter(score) # type: ignore
        except TypeError:
            return score # type: ignore 
        else:
            return next(iterator) 
