from enum import Enum
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from lib.db import DB
from datetime import datetime, timezone
from flask import current_app
from lib import utils
import pickle

class NoTraingDataError(Exception):
    pass

class TrainingIntervalError(Exception):
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
    "WeatherConditions",
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
        "NIGHT_RAIN_AND_FOG",
        "FOG",
        "NIGHT_FOG",
        "MOSTLY_CLEAR",
        "NIGHT_MOSTLY_CLEAR",
        "BRIEF_SHOWERS_POSSIBLE",
        "NIGHT_BRIEF_SHOWERS_POSSIBLE",
        "HEAVY_SHOWERS",
        "NIGHT_HEAVY_SHOWERS",
    ],
)


def predict(spot_report, rating_forecast, weather_forecast, tides_forecast, wave_forecast, wind_forecast):
    """
    Given a spot_id, spot_forecast + weather_forecast.
    predict the crowd count for each day
    """
    model = Model.load()
    spot_forecast = spot_report["forecast"]


    predictions = []
    for rating, weather, wind, wave, tide  in zip(rating_forecast, weather_forecast, wind_forecast, wave_forecast, tides_forecast):
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

        # this isn't provided hour by hour.
        # So we just take the spot daily forecast
        water_temp_max = spot_forecast["waterTemp"]["max"]
        water_temp_min = spot_forecast["waterTemp"]["min"]

        wave_height_max = wave["surf"]["max"] 
        wave_height_min = wave["surf"]["min"] 
        wind_direction = wind["direction"]
        wind_speed = wind["speed"] 
        wind_gust = wind["gust"] 
        tide_height = tide["height"]

        if "NIGHT" in weather_condition:
            # We don't record at night
            # so we don't care about predictions.
            # But also "night" changes between
            # spots so we use the weather label
            # to determine this.
            crowd_count_predicted = 0
        else:
            crowd_count_predicted = model.predict(
                rating_value,
                weather_temperature,
                weather_condition_value,
                weekday,
                hour,
                water_temp_max,
                water_temp_min,
                wave_height_max,
                wave_height_min,
                wind_direction,
                wind_speed,
                wind_gust,
                tide_height
            )

        crowd_count_predicted = round(crowd_count_predicted, 2)

        if crowd_count_predicted < 0:
            crowd_count_predicted = 0 

        predictions.append(
            {
                "timestamp_utc": ts,
                "timestamp_local": local_ts,
                "surf_rating": rating_name,
                "crowd_count_predicted": crowd_count_predicted,
            }
        )

    return predictions


def train():
    """
    Loads any new data since last training.
    trains the model
    persists it model to disk
    logs a training event with new score.
    """
    model = Model.load()

    db = DB.get_db()
    latest_log = db.latest_training_log(Model.get_url())
    since = latest_log["timestamp"] if latest_log else None
    training_interval = current_app.config["INTERVAL_TRAINING"]

    if since:
        seconds_since_last_train = (datetime.utcnow() - datetime.strptime(since, utils.DATETIME_FORMAT) ).total_seconds()
        if seconds_since_last_train < training_interval:
            raise TrainingIntervalError(f"Not training model last_training is within training interval: {training_interval} only {seconds_since_last_train} seconds have passed.") 

    x_train, x_test, y_train, y_test = model.get_training_data()

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
        self.labels = [
            "surf_rating",
            "weather_temp",
            "weather_condition",
            "weekday",
            "hour",
            "water_temp_max",
            "water_temp_min",
            "wave_height_max",
            "wave_height_min",
            "wind_direction",
            "wind_speed",
            "wind_gust", 
            "tide_height"
        ]
        self.m = RandomForestRegressor(random_state=42)

    def get_training_data(self, test_size=None, random_state=None):
        """
        Get todays new training data
        then split it by test/training.
        """
        SURFLINE_SPOT_ID = current_app.config.get("SURFLINE_SPOT_ID")

        db = DB.get_db()
        logs = db.logs(SURFLINE_SPOT_ID)

        if not logs:
            raise NoTraingDataError("No training data available")

        feature = "crowd_count"

        x_data = []
        y_data = []

        for log in logs:
            x = []
            y = 0

            for key, value in log.items():
                if key in self.labels:
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
        return train_test_split(
            X,
            Y,
            test_size=test_size,
            random_state=random_state,
        )

    @staticmethod
    def get_url() -> str:
        return current_app.config["MODEL_URL"]

    @staticmethod
    def load():
        """
        load for inference 
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
        with open(current_app.config["MODEL_URL"], "wb") as f:
            pickle.dump(self, f)

    def train(self, x_train, y_train):
        self.m.fit(x_train, y_train)

    def predict(
        self,
        *args,
    ) -> float:
        prediction = self.m.predict(
            [args]
        )
        try:
            iterator = iter(prediction)  # type: ignore
        except TypeError:
            return prediction # type: ignore
        else:
            return next(iterator)

    def score(self, x_test, y_test) -> float:
        score = self.m.score(x_test, y_test)
        try:
            iterator = iter(score)  # type: ignore
        except TypeError:
            return score  # type: ignore
        else:
            return next(iterator)
