from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy インスタンス（アプリ全体で共有）
db = SQLAlchemy()


def init_db(app):
    """アプリケーションに DB を初期化する"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
