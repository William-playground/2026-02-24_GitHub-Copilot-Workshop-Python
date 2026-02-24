import sys
import os
import pytest

# 1.pomodoro をモジュール検索パスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import TestingConfig
from app import create_app
from database import db as _db


@pytest.fixture()
def app():
    """テスト用 Flask アプリケーション"""
    app = create_app(TestingConfig)
    yield app


@pytest.fixture()
def db(app):
    """テスト用データベース（各テストで初期化）"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()
