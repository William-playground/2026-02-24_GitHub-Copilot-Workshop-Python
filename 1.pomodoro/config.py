import os


class Config:
    """本番用設定"""
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'pomodoro.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY")


class TestingConfig(Config):
    """テスト用設定（インメモリ DB）"""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
