from flask import Flask, render_template, request, jsonify
from config import Config
from database import init_db
from repositories.session_repo import SessionRepository
from services.session_service import SessionService


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

    # サービス初期化
    repo = SessionRepository()
    service = SessionService(repo)

    # ルート定義
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/session", methods=["POST"])
    def create_session():
        data = request.get_json() or {}
        duration = data.get("duration", 1500)
        session_type = data.get("type", "work")
        result = service.complete_session(duration=duration, session_type=session_type)
        return jsonify(result), 201

    @app.route("/api/stats/today", methods=["GET"])
    def today_stats():
        stats = service.get_today_stats()
        return jsonify(stats)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
