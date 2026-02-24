from flask import Blueprint, jsonify, request

from database import db
from models import Settings
from services.session_service import SessionService

api = Blueprint("api", __name__, url_prefix="/api")
session_service = SessionService()


@api.route("/session", methods=["POST"])
def create_session():
    data = request.get_json(silent=True) or {}
    duration = data.get("duration", 25)
    if not isinstance(duration, int) or duration <= 0:
        return jsonify({"error": "duration must be a positive integer"}), 400
    result = session_service.complete_session(duration)
    return jsonify(result), 201


@api.route("/stats/today", methods=["GET"])
def stats_today():
    stats = session_service.get_today_stats()
    return jsonify(stats)


@api.route("/settings", methods=["GET", "POST"])
def settings():
    row = Settings.query.first()
    if request.method == "GET":
        if row is None:
            return jsonify({"work_duration": 25, "break_duration": 5})
        return jsonify(row.to_dict())

    data = request.get_json(silent=True) or {}
    work = data.get("work_duration", 25)
    brk = data.get("break_duration", 5)
    if not isinstance(work, int) or work <= 0:
        return jsonify({"error": "work_duration must be a positive integer"}), 400
    if not isinstance(brk, int) or brk <= 0:
        return jsonify({"error": "break_duration must be a positive integer"}), 400

    if row is None:
        row = Settings(work_duration=work, break_duration=brk)
        db.session.add(row)
    else:
        row.work_duration = work
        row.break_duration = brk
    db.session.commit()
    return jsonify(row.to_dict())
