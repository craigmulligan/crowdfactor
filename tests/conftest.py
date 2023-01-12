from unittest.mock import Mock
from lib.app import app as flask_app
from lib import forecast
from lib.db import DB
from lib.seed import seed as seed_db, seed_training_data as seed_db_training_data
import pytest
from datetime import datetime, timezone
import tempfile, os, uuid
import requests_mock
import json

@pytest.fixture()
def mock_forecast(monkeypatch, spot_id):
    mock = Mock(wraps=forecast.get_latest)
    monkeypatch.setattr(forecast, "get_latest", mock)

    with open(os.path.join("tests", "data", f"rating-{spot_id}.json")) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(f"https://services.surfline.com/kbyg/spots/forecasts/rating?spotId={spot_id}&days=1&intervalHours=1", json=data)
        yield mock


@pytest.fixture()
def mock_spot_info(spot_id, monkeypatch):
    mock = Mock(wraps=forecast.get_spot_info)
    monkeypatch.setattr(forecast, "get_spot_info", mock)

    with open(os.path.join("tests", "data", f"spot-info-{spot_id}.json")) as f, requests_mock.Mocker(real_http=True) as m:
        data = json.load(f)
        m.get(f"https://services.surfline.com/kbyg/spots/reports?spotId={spot_id}&corrected=false", json=data)
        yield

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
    cache_filename = os.path.join(tempfile.gettempdir(), str(uuid.uuid1()))
    model_filename = os.path.join(tempfile.gettempdir(), str(uuid.uuid1()))

    flask_app.config.update(
        {
            "TESTING": True,
            "DB_URL": ":memory:",
            "CACHE_URL": cache_filename,
            "MODEL_URL": model_filename,
            "SURFLINE_SPOT_ID": spot_id,
            "ROBOFLOW_API_KEY": "xyz",
        }
    )
    ctx = flask_app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

        for f in [cache_filename, model_filename]:
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
    seed_db(spot_id, *seed_window)
