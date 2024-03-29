from unittest.mock import Mock
from lib.app import app as flask_app
from lib import forecast
from lib.db import DB
from lib.seed import seed as seed_db
from lib.ml import Model
from lib.cache import cache
import pytest
from datetime import datetime, timezone
import tempfile, os, uuid
import requests_mock
import json


@pytest.fixture()
def mock_surf_rating_forecast(monkeypatch, spot_id):
    mock = Mock(wraps=forecast.get_spot_surf_rating)
    monkeypatch.setattr(forecast, "get_spot_surf_rating", mock)

    with open(
        os.path.join("tests", "data", f"rating-{spot_id}.json")
    ) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(
            f"https://services.surfline.com/kbyg/spots/forecasts/rating?spotId={spot_id}&days=1&intervalHours=1",
            json=data,
        )
        yield mock


@pytest.fixture()
def mock_weather_forecast(monkeypatch, spot_id):
    mock = Mock(wraps=forecast.get_spot_weather)
    monkeypatch.setattr(forecast, "get_spot_weather", mock)

    with open(
        os.path.join("tests", "data", f"weather-{spot_id}.json")
    ) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(
            f"https://services.surfline.com/kbyg/spots/forecasts/weather?spotId={spot_id}&days=1&intervalHours=1",
            json=data,
        )
        yield mock


@pytest.fixture()
def mock_wave_forecast(monkeypatch, spot_id):
    mock = Mock(wraps=forecast.get_spot_wave)
    monkeypatch.setattr(forecast, "get_spot_wave", mock)

    with open(
        os.path.join("tests", "data", f"wave-{spot_id}.json")
    ) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(
            f"https://services.surfline.com/kbyg/spots/forecasts/wave?spotId={spot_id}&days=1&intervalHours=1",
            json=data,
        )
        yield mock


@pytest.fixture()
def mock_wind_forecast(monkeypatch, spot_id):
    mock = Mock(wraps=forecast.get_spot_wind)
    monkeypatch.setattr(forecast, "get_spot_wind", mock)

    with open(
        os.path.join("tests", "data", f"wind-{spot_id}.json")
    ) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(
            f"https://services.surfline.com/kbyg/spots/forecasts/wind?spotId={spot_id}&days=1&intervalHours=1",
            json=data,
        )
        yield mock


@pytest.fixture()
def mock_tides_forecast(monkeypatch, spot_id):
    mock = Mock(wraps=forecast.get_spot_tides)
    monkeypatch.setattr(forecast, "get_spot_tides", mock)

    with open(
        os.path.join("tests", "data", f"tides-{spot_id}.json")
    ) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(
            f"https://services.surfline.com/kbyg/spots/forecasts/tides?spotId={spot_id}&days=1&intervalHours=1",
            json=data,
        )
        yield mock


@pytest.fixture()
def mock_forecasts(
    mock_surf_rating_forecast,
    mock_weather_forecast,
    mock_tides_forecast,
    mock_wave_forecast,
    mock_wind_forecast,
):
    return (
        mock_surf_rating_forecast,
        mock_weather_forecast,
        mock_tides_forecast,
        mock_wave_forecast,
        mock_wind_forecast,
    )


@pytest.fixture()
def mock_spot_report(spot_id, monkeypatch):
    mock = Mock(wraps=forecast.get_spot_report)
    monkeypatch.setattr(forecast, "get_spot_report", mock)

    with open(
        os.path.join("tests", "data", f"spot-info-{spot_id}.json")
    ) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(
            f"https://services.surfline.com/kbyg/spots/reports?spotId={spot_id}&corrected=false",
            json=data,
        )
        yield mock


@pytest.fixture()
def mock_spot_info(spot_id, monkeypatch, mock_spot_report):
    mock = Mock(wraps=forecast.get_spot_info)
    monkeypatch.setattr(forecast, "get_spot_info", mock)
    yield mock


@pytest.fixture(scope="session")
def spot_id():
    return "590927576a2e4300134fbed8"


@pytest.fixture()
def surfline_url(spot_id):
    return f"https://www.surfline.com/surf-report/venice-breakwater/{spot_id}?camId=5834a1b6e411dc743a5d52f3"


@pytest.fixture()
def app(request, spot_id):
    """Session-wide test `Flask` application."""
    # Establish an application context before running the tests.
    model_filename = os.path.join(tempfile.gettempdir(), str(uuid.uuid1()))
    db_url = os.environ.get("DB_URL", ":memory:")

    flask_app.config.update(
        {
            "TESTING": True,
            "DB_URL": db_url,
            "MODEL_URL": model_filename,
            "SURFLINE_SPOT_ID": spot_id,
            "ROBOFLOW_API_KEY": "xyz",
            "CACHE_TYPE": "SimpleCache",
        }
    )
    ctx = flask_app.app_context()
    ctx.push()

    def teardown():
        cache.clear()
        ctx.pop()

        for f in [model_filename]:
            if os.path.exists(f):
                os.remove(f)

    request.addfinalizer(teardown)
    return flask_app


@pytest.fixture(autouse=True)
def db(app):
    """per test database."""
    db = DB.get_db()
    db.setup()
    return db


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seed_window():
    start = datetime(2021, 1, 1, tzinfo=timezone.utc)
    end = datetime(2021, 12, 31, tzinfo=timezone.utc)
    return (start, end)


@pytest.fixture()
def seed(spot_id, seed_window):
    """
    seed the db with dummy data.
    """
    rows = seed_db(spot_id, *seed_window)
    return rows


@pytest.fixture()
def pretrained_model(seed):
    model = Model.load()
    x_train, x_test, y_train, y_test = model.get_training_data(random_state=1)
    model.train(x_train, y_train)
    model.persist()
    return model
