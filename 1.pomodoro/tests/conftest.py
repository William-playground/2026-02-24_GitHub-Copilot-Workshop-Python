import pytest

from app import create_app
from config import TestingConfig
from database import db as _db


@pytest.fixture()
def app():
    app = create_app(TestingConfig)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()
