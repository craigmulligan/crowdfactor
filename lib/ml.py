from enum import Enum
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from lib.db import DB
from flask import current_app

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
    def __init__(self, name) -> None:
        self.m = LinearRegression() 
        self.name = name

    @staticmethod
    def get_training_data(test_size=None, random_state=None):
        # TODO. Save model to disk.
        # load it back and then retrain on new data.
        # see: 
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
    def load(name: str):
        return Model(name)

    def persist(self):
        pass

    def train(self, x_train, y_train):
        self.m.fit(x_train, y_train)

    def score(self, x_test, y_test):
        score = self.m.score(x_test, y_test)
        try:
            iterator = iter(score) # type: ignore
        except TypeError:
            return score
        else:
            return next(iterator) 

