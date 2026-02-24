import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from config import TestingConfig
from database import db


@pytest.fixture()
def app():
    return create_app(TestingConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_title(client):
    response = client.get("/")
    assert b"Pomodoro Timer" in response.data


def test_session_model_exists(app):
    with app.app_context():
        from models import Session

        assert Session.__tablename__ == "sessions"


def test_database_tables_created(app):
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        assert "sessions" in tables
