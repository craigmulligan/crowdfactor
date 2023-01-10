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


def train():
    """
    trains the model.
    """

    # TODO. Save model to disk.
    # load it back and then retrain on new data.
    # see: https://stackoverflow.com/questions/46286669/how-to-retrain-logistic-regression-model-in-sklearn-with-new-data
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

    x_train, x_test, y_train, y_test = train_test_split(
     X, Y
    )

    model = LinearRegression().fit(x_train, y_train)
    r_sq = model.score(x_test, y_test)
    prediction = model.predict([x_data[0]])
    print(f"coefficient of determination: {r_sq}")
    print(f"prediction: {prediction}")
