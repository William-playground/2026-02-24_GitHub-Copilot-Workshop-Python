# Pomodoro Timer App
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
    app.run(debug=True, port=5000)
