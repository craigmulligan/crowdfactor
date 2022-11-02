from lib.app import app as flask_app
from lib.db import DB
from lib.seed import seed as seed_db
import random
import pytest


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
