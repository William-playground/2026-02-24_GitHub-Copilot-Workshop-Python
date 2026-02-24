"""Pomodoro Timer App — Flask バックエンド."""

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# --- インメモリ状態 -----------------------------------------------------------
_state = {
    "completed": 0,
    "total_focus_minutes": 0,
}


# --- ページ配信 ---------------------------------------------------------------
@app.route("/")
def index():
    """メインページを返す."""
    return render_template("index.html")


# --- API ----------------------------------------------------------------------
@app.route("/api/status", methods=["GET"])
def api_status():
    """現在の進捗を返す."""
    return jsonify(_state)


@app.route("/api/complete", methods=["POST"])
def api_complete():
    """作業セッション完了を記録する."""
    data = request.get_json(silent=True) or {}
    minutes = data.get("minutes", 25)
    if not isinstance(minutes, (int, float)) or minutes < 0:
        return jsonify({"error": "invalid minutes"}), 400
    _state["completed"] += 1
    _state["total_focus_minutes"] += int(minutes)
    return jsonify(_state)


@app.route("/api/reset_progress", methods=["POST"])
def api_reset_progress():
    """今日の進捗をリセットする."""
    _state["completed"] = 0
    _state["total_focus_minutes"] = 0
    return jsonify(_state)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
