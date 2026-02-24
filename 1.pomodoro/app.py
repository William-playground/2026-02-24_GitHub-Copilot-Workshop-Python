# Pomodoro Timer App
import os

from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main Pomodoro Timer page."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true", port=5000)
