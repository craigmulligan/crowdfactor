from lib.app import app as flask_app
from lib.db import DB
import random
import pytest


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
def seed(db):
    """
    seed the db with dummy data.
    """
    # for range over the 3rd to 10th oct.
    # which is Monday-Sunday
    for d in range(3, 10):
        for h in range(24):
            # for each hour in the day.
            db.insert(
                h,  # make crowd count equal to hour so it's easy to assert.
                "FAIR",
                f"2022-10-{d:02}T{h}:00:00",
            )
