# Pomodoro Timer App
from flask import Flask, jsonify, request, render_template
from datetime import datetime, timezone, timedelta
from models import db, PomodoroSession, UserProfile, Badge


# Badge definitions: (name, description, check_function)
BADGE_DEFINITIONS = [
    {
        "name": "初めてのポモドーロ",
        "description": "最初のポモドーロを完了しました",
        "icon": "🍅",
    },
    {
        "name": "5回達成",
        "description": "ポモドーロを5回完了しました",
        "icon": "⭐",
    },
    {
        "name": "10回達成",
        "description": "ポモドーロを10回完了しました",
        "icon": "🌟",
    },
    {
        "name": "3日連続",
        "description": "3日連続でポモドーロを完了しました",
        "icon": "🔥",
    },
    {
        "name": "7日連続",
        "description": "7日連続でポモドーロを完了しました",
        "icon": "💎",
    },
    {
        "name": "今週10回完了",
        "description": "今週ポモドーロを10回完了しました",
        "icon": "🏆",
    },
]


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pomodoro.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        _ensure_user_profile()

    register_routes(app)
    return app


def _ensure_user_profile():
    """Ensure a single UserProfile row exists."""
    profile = db.session.get(UserProfile, 1)
    if not profile:
        profile = UserProfile(id=1, xp=0, level=1)
        db.session.add(profile)
        db.session.commit()


def _get_profile():
    return db.session.get(UserProfile, 1)


def _calculate_xp(duration_minutes):
    """XP per pomodoro = 10 * (duration_minutes / 25), rounded to int."""
    return round(10 * (duration_minutes / 25))


def _calculate_level(xp):
    """Level = 1 + (total_xp // 100)."""
    return 1 + (xp // 100)


def _xp_to_next_level(xp):
    """XP needed to reach next level = 100 - (xp % 100)."""
    return 100 - (xp % 100)


def _get_streak_info():
    """Calculate current and best streak from session history."""
    sessions = (
        PomodoroSession.query.order_by(PomodoroSession.completed_at.desc()).all()
    )

    if not sessions:
        return {"current_streak": 0, "best_streak": 0}

    # Collect unique dates (UTC) that have sessions
    session_dates = set()
    for s in sessions:
        session_dates.add(s.completed_at.date())

    if not session_dates:
        return {"current_streak": 0, "best_streak": 0}

    sorted_dates = sorted(session_dates, reverse=True)
    today = datetime.now(timezone.utc).date()

    # Current streak: consecutive days going back from today
    current_streak = 0
    check_date = today
    for _ in range(len(sorted_dates) + 1):
        if check_date in session_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    # Best streak: find longest consecutive run in all dates
    all_sorted = sorted(session_dates)
    best_streak = 0
    run = 1
    for i in range(1, len(all_sorted)):
        if (all_sorted[i] - all_sorted[i - 1]).days == 1:
            run += 1
        else:
            best_streak = max(best_streak, run)
            run = 1
    best_streak = max(best_streak, run)

    return {"current_streak": current_streak, "best_streak": best_streak}


def _get_weekly_session_count():
    """Count sessions in the current ISO week (Mon-Sun)."""
    now = datetime.now(timezone.utc)
    # Monday of current week
    monday = now.date() - timedelta(days=now.weekday())
    monday_dt = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
    count = PomodoroSession.query.filter(
        PomodoroSession.completed_at >= monday_dt
    ).count()
    return count


def _check_consecutive_days(required_days):
    """Check if there are `required_days` consecutive days with sessions."""
    sessions = PomodoroSession.query.all()
    if not sessions:
        return False

    session_dates = set()
    for s in sessions:
        session_dates.add(s.completed_at.date())

    if len(session_dates) < required_days:
        return False

    sorted_dates = sorted(session_dates)
    run = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            run += 1
            if run >= required_days:
                return True
        else:
            run = 1

    return run >= required_days


def _check_and_award_badges():
    """Check all badge conditions and award any newly earned badges."""
    newly_earned = []
    total_sessions = PomodoroSession.query.count()

    badge_checks = [
        ("初めてのポモドーロ", lambda: total_sessions >= 1),
        ("5回達成", lambda: total_sessions >= 5),
        ("10回達成", lambda: total_sessions >= 10),
        ("3日連続", lambda: _check_consecutive_days(3)),
        ("7日連続", lambda: _check_consecutive_days(7)),
        ("今週10回完了", lambda: _get_weekly_session_count() >= 10),
    ]

    for badge_name, check_fn in badge_checks:
        existing = Badge.query.filter_by(name=badge_name).first()
        if not existing and check_fn():
            # Find description from BADGE_DEFINITIONS
            defn = next(
                (b for b in BADGE_DEFINITIONS if b["name"] == badge_name), None
            )
            description = defn["description"] if defn else ""
            badge = Badge(name=badge_name, description=description)
            db.session.add(badge)
            newly_earned.append(badge_name)

    if newly_earned:
        db.session.commit()

    return newly_earned


def _get_all_badges_status():
    """Return all badges with their earned status."""
    earned_badges = {b.name: b for b in Badge.query.all()}
    result = []
    for defn in BADGE_DEFINITIONS:
        earned = defn["name"] in earned_badges
        badge_info = {
            "name": defn["name"],
            "description": defn["description"],
            "icon": defn["icon"],
            "earned": earned,
        }
        if earned:
            badge_info["earned_at"] = earned_badges[defn["name"]].earned_at.isoformat()
        result.append(badge_info)
    return result


def register_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/sessions", methods=["POST"])
    def create_session():
        data = request.get_json(silent=True) or {}
        duration = data.get("duration_minutes", 25)

        session = PomodoroSession(duration_minutes=duration)
        db.session.add(session)
        db.session.commit()

        # Award XP
        profile = _get_profile()
        xp_earned = _calculate_xp(duration)
        profile.xp += xp_earned
        profile.level = _calculate_level(profile.xp)
        db.session.commit()

        # Check badges
        new_badges = _check_and_award_badges()

        return jsonify(
            {
                "session": {
                    "id": session.id,
                    "duration_minutes": session.duration_minutes,
                    "completed_at": session.completed_at.isoformat(),
                },
                "xp_earned": xp_earned,
                "total_xp": profile.xp,
                "level": profile.level,
                "xp_to_next_level": _xp_to_next_level(profile.xp),
                "new_badges": new_badges,
            }
        ), 201

    @app.route("/api/sessions", methods=["GET"])
    def list_sessions():
        sessions = PomodoroSession.query.order_by(
            PomodoroSession.completed_at.desc()
        ).all()
        return jsonify(
            [
                {
                    "id": s.id,
                    "duration_minutes": s.duration_minutes,
                    "completed_at": s.completed_at.isoformat(),
                }
                for s in sessions
            ]
        )

    @app.route("/api/gamification", methods=["GET"])
    def gamification():
        profile = _get_profile()
        streak = _get_streak_info()
        badges = _get_all_badges_status()

        # Weekly/monthly stats summary
        now = datetime.now(timezone.utc)
        week_start = now.date() - timedelta(days=now.weekday())
        week_start_dt = datetime(
            week_start.year, week_start.month, week_start.day, tzinfo=timezone.utc
        )
        month_start_dt = now - timedelta(days=30)

        weekly_count = PomodoroSession.query.filter(
            PomodoroSession.completed_at >= week_start_dt
        ).count()
        monthly_count = PomodoroSession.query.filter(
            PomodoroSession.completed_at >= month_start_dt
        ).count()

        return jsonify(
            {
                "xp": profile.xp,
                "level": profile.level,
                "xp_to_next_level": _xp_to_next_level(profile.xp),
                "badges": badges,
                "streak": streak,
                "weekly_sessions": weekly_count,
                "monthly_sessions": monthly_count,
            }
        )

    @app.route("/api/stats", methods=["GET"])
    def stats():
        now = datetime.now(timezone.utc)

        # Weekly stats: last 7 days, sessions per day
        weekly = []
        for i in range(6, -1, -1):
            day = now.date() - timedelta(days=i)
            day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)
            count = PomodoroSession.query.filter(
                PomodoroSession.completed_at >= day_start,
                PomodoroSession.completed_at < day_end,
            ).count()
            weekly.append(
                {
                    "date": day.isoformat(),
                    "sessions": count,
                }
            )

        # Monthly stats: last 30 days
        month_start = now - timedelta(days=30)
        monthly_sessions = PomodoroSession.query.filter(
            PomodoroSession.completed_at >= month_start
        ).all()
        total_monthly = len(monthly_sessions)
        avg_duration = 0.0
        if total_monthly > 0:
            avg_duration = sum(s.duration_minutes for s in monthly_sessions) / total_monthly

        # Completion rate: based on 8 pomodoros/day goal over 30 days
        goal_total = 8 * 30
        completion_rate = round((total_monthly / goal_total) * 100, 1) if goal_total > 0 else 0.0

        return jsonify(
            {
                "weekly": weekly,
                "monthly": {
                    "total_sessions": total_monthly,
                    "average_duration": round(avg_duration, 1),
                    "completion_rate": completion_rate,
                },
            }
        )


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
