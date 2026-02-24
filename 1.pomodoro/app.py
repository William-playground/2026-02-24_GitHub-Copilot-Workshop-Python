# Pomodoro Timer App

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Default settings stored in memory
settings = {
    "work_duration": 25,
    "break_duration": 5,
    "theme": "dark",
    "sound_start": True,
    "sound_end": True,
    "sound_tick": False,
}

VALID_WORK_DURATIONS = [15, 25, 35, 45]
VALID_BREAK_DURATIONS = [5, 10, 15]
VALID_THEMES = ["dark", "light", "focus"]


def validate_settings(data):
    """Validate incoming settings. Returns (errors, validated_fields) tuple."""
    errors = []
    validated = {}

    if "work_duration" in data:
        val = data["work_duration"]
        if val not in VALID_WORK_DURATIONS:
            errors.append(
                f"work_duration must be one of {VALID_WORK_DURATIONS}"
            )
        else:
            validated["work_duration"] = val

    if "break_duration" in data:
        val = data["break_duration"]
        if val not in VALID_BREAK_DURATIONS:
            errors.append(
                f"break_duration must be one of {VALID_BREAK_DURATIONS}"
            )
        else:
            validated["break_duration"] = val

    if "theme" in data:
        val = data["theme"]
        if val not in VALID_THEMES:
            errors.append(f"theme must be one of {VALID_THEMES}")
        else:
            validated["theme"] = val

    for sound_key in ["sound_start", "sound_end", "sound_tick"]:
        if sound_key in data:
            val = data[sound_key]
            if not isinstance(val, bool):
                errors.append(f"{sound_key} must be a boolean")
            else:
                validated[sound_key] = val

    return errors, validated


@app.route("/")
def index():
    """Render the main timer page."""
    return render_template("index.html")


@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Return current settings as JSON."""
    return jsonify(settings)


@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Update settings from JSON body. Supports partial updates."""
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    errors, validated = validate_settings(data)
    if errors:
        return jsonify({"errors": errors}), 400

    settings.update(validated)
    return jsonify(settings)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
