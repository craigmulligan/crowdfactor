from enum import Enum
import numpy as np
from sklearn.linear_model import PassiveAggressiveRegressor
from sklearn.model_selection import train_test_split
from lib.db import DB
from datetime import datetime, timezone
from flask import current_app
from lib import utils
import pickle

class NoTraingDataError(Exception):
    pass

# Note always add to the end of Enum
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

# Note always add to the end of Enum
WeatherConditions = Enum(
    "SurfRating",
    [
        "NIGHT_CLEAR",
        "NIGHT_MIST",
        "NIGHT_LIGHT_SHOWERS",
        "NIGHT_MOSTLY_CLOUDY",
        "NIGHT_BRIEF_SHOWERS",
        "NIGHT_OVERCAST",
        "NIGHT_CLOUDY",
        "NIGHT_DRIZZLE",
        "CLEAR",
        "MIST",
        "LIGHT_SHOWERS",
        "MOSTLY_CLOUDY",
        "BRIEF_SHOWERS",
        "OVERCAST",
        "CLOUDY",
        "DRIZZLE",
        "NIGHT_LIGHT_RAIN",
        "LIGHT_RAIN",
        "RAIN",
        "NIGHT_RAIN",
        "HEAVY_RAIN", 
        "NIGHT_HEAVY_RAIN",
        "RAIN_AND_FOG",
        "NIGHT_RAIN_AND_FOG"
    ],
)

def predict(rating_forecast, weather_forecast):
    """
    Given a spot_id, spot_forecast + weather_forecast.
    predict the crowd count for each day
    """
    model = Model.load()
    if len(rating_forecast) != len(weather_forecast):
        raise Exception("Forecasts are not the same length.")

    predictions = []
    for rating, weather in zip(rating_forecast, weather_forecast): 
        ts = datetime.utcfromtimestamp(rating["timestamp"]).replace(tzinfo=timezone.utc)
        weekday = ts.isoweekday()
        offset = rating["utcOffset"]
        local_ts = utils.local_timestamp(ts, offset)
        hour = ts.hour
        rating_name = rating["rating"]["key"]
        rating_value = SurfRating[rating_name].value

        weather_temperature = weather["temperature"] 
        weather_condition = weather["condition"]
        weather_condition_value = WeatherConditions[weather_condition].value

        if "NIGHT" in weather_condition:
            # We don't record at night
            # so we don't care about predictions.
            # But also "night" changes between
            # spots so we use the weather label 
            # to determine this.
            crowd_count_predicted = 0
        else:
            crowd_count_predicted = model.predict(rating_value, weather_temperature, weather_condition_value, weekday, hour)

        predictions.append({
            "timestamp_utc": ts,  
            "timestamp_local": local_ts,
            "surf_rating": rating_name,
            "crowd_count_predicted": round(crowd_count_predicted)
        })

    return predictions

def train():
    """
    Loads any new data since last training. 
    trains the model
    persists it model to disk
    logs a training event with new score.
    """
    try:
        x_train, x_test, y_train, y_test = Model.get_training_data()
    except NoTraingDataError:
        return False

    model = Model.load()
    model.train(x_train, y_train)

    model.persist()
    score = model.score(x_test, y_test)
    model.log(score)
    return True


class Model:
    """
    A model that can be incrementally retrained.
    see: https://datascience.stackexchange.com/questions/68599/incremental-learning-with-sklearn-warm-start-partial-fit-fit
    """
    def __init__(self) -> None:
        # Note we set random_state here.
        # So we have consistent results for testing.
        # I assume we want to remove this when not in tests.
        self.m = PassiveAggressiveRegressor(warm_start=True)

    @staticmethod
    def get_training_data(test_size=None, random_state=None):
        """
        Get todays new training data
        then split it by test/training. 
        """
        SURFLINE_SPOT_ID = current_app.config.get("SURFLINE_SPOT_ID")

        db = DB.get_db()
        latest_log = db.latest_training_log(Model.get_url())
        since = latest_log["timestamp"] if latest_log else None
        logs = db.logs(SURFLINE_SPOT_ID, since)

        if not logs:
            raise NoTraingDataError("No training data")

        labels = ["surf_rating", "weather_temp", "weather_condition",  "weekday", "hour"]
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
                    elif key == "weather_condition":
                       x.append(WeatherConditions[value].value) 
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
    def get_url() -> str:
        return current_app.config["MODEL_URL"]

    @staticmethod
    def load():
        """
        We might change it to read the old model if we need to do 
        incremental learning at some point.
        """
        try:
            with open(Model.get_url(),'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
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
            pickle.dump(self, f)

    def train(self, x_train, y_train):
        self.m.partial_fit(x_train, y_train)

    def predict(self, surf_rating: int, weather_temp: int, weather_condition: int,  weekday: int, hour: int) -> float:
        prediction = self.m.predict([[surf_rating, weather_temp, weather_condition, weekday, hour]])
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
