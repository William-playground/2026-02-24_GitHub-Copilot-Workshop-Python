import sys
import os
import pytest

# 1.pomodoro ディレクトリをインポートパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from config import TestingConfig
from database import db as _db


@pytest.fixture()
def app():
    """テスト用 Flask アプリケーション（インメモリ DB）"""
    app = create_app(config=TestingConfig)
    yield app


@pytest.fixture()
def client(app):
    """Flask テストクライアント"""
    return app.test_client()


@pytest.fixture()
def db(app):
    """テスト用データベース（テストごとにリセット）"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
