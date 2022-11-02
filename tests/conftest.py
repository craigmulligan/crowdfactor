from unittest.mock import Mock
from lib.app import app as flask_app
from lib import forecast
from lib.db import DB
from lib.seed import seed as seed_db
import pytest
from datetime import date, datetime, timedelta
import time


@pytest.fixture()
def mock_forecast(monkeypatch):
    today = datetime.combine(date.today(), datetime.min.time())
    intervals = [(today + timedelta(hours=x)) for x in range(24)]
    data = []

    for i, ts in enumerate(intervals):
        condition = "FAIR"

        if i > 5:
            condition = "GOOD"

        data.append(
            {
                "timestamp": int(ts.timestamp()),
                "utcOffset": 0,  # TODO need to handle timezones
                "rating": {
                    "key": condition,
                },
            }
        )

    mock = Mock(return_value=data)
    monkeypatch.setattr(forecast, "get_latest", mock)
    yield mock


@pytest.fixture()
def spot_id():
    return "1234"


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    # Establish an application context before running the tests.
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    ctx = flask_app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return flask_app


@pytest.fixture(scope="session", autouse=True)
def db(app):
    """Session-wide test database."""
    db = DB.get_db()
    db.setup()
    return db


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seed(db, spot_id):
    """
    seed the db with dummy data.
    """
    seed_db(spot_id)
