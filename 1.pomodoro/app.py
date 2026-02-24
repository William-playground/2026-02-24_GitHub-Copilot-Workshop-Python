from flask import Flask, render_template
from config import Config
from database import init_db


def create_app(config=None):
    """アプリケーションファクトリ"""
    app = Flask(__name__)

    # 設定を読み込む（デフォルトは Config）
    if config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config)

    # DB 初期化
    init_db(app)

    # ルート定義
    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
