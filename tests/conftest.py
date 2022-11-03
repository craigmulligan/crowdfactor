from unittest.mock import Mock
from lib.app import app as flask_app
from lib import forecast
from lib.db import DB
from lib.seed import seed as seed_db
import pytest
from datetime import date, datetime, timedelta


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
                "utcOffset": -7,
                "rating": {
                    "key": condition,
                },
            }
        )

    mock = Mock(return_value=data)
    monkeypatch.setattr(forecast, "get_latest", mock)
    yield mock


@pytest.fixture(scope="session")
def spot_id():
    return "590927576a2e4300134fbed8"


@pytest.fixture()
def surfline_url(spot_id):
    return f"https://www.surfline.com/surf-report/venice-breakwater/{spot_id}?camId=5834a1b6e411dc743a5d52f3"


@pytest.fixture(scope="session")
def app(request, spot_id):
    """Session-wide test `Flask` application."""
    # Establish an application context before running the tests.
    flask_app.config.update(
        {
            "TESTING": True,
            "DB_URL": ":memory:",
            "SURFLINE_SPOT_ID": spot_id,
            "ROBOFLOW_API_KEY": "xyz",
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
def seed(spot_id):
    """
    seed the db with dummy data.
    """
    seed_db(spot_id)
