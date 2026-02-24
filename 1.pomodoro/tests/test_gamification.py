import json
from datetime import datetime, timezone, timedelta
from models import PomodoroSession, UserProfile, Badge


class TestPostSession:
    """Test POST /api/sessions creates a session and awards XP."""

    def test_create_session_default_duration(self, client, db):
        resp = client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["session"]["duration_minutes"] == 25
        assert data["xp_earned"] == 10
        assert data["total_xp"] == 10
        assert data["level"] == 1

    def test_create_session_custom_duration(self, client, db):
        resp = client.post(
            "/api/sessions",
            data=json.dumps({"duration_minutes": 50}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["session"]["duration_minutes"] == 50
        assert data["xp_earned"] == 20

    def test_session_stored_in_database(self, client, db, app):
        client.post(
            "/api/sessions",
            data=json.dumps({"duration_minutes": 25}),
            content_type="application/json",
        )
        with app.app_context():
            sessions = PomodoroSession.query.all()
            assert len(sessions) == 1
            assert sessions[0].duration_minutes == 25


class TestXPAndLevel:
    """Test XP and level calculations."""

    def test_xp_accumulates(self, client, db):
        for _ in range(5):
            client.post(
                "/api/sessions",
                data=json.dumps({}),
                content_type="application/json",
            )
        resp = client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = resp.get_json()
        # 6 sessions * 10 XP = 60
        assert data["total_xp"] == 60
        assert data["level"] == 1

    def test_level_up_at_100xp(self, client, db):
        for _ in range(10):
            resp = client.post(
                "/api/sessions",
                data=json.dumps({}),
                content_type="application/json",
            )
        data = resp.get_json()
        # 10 * 10 = 100 XP -> level 2
        assert data["total_xp"] == 100
        assert data["level"] == 2

    def test_xp_to_next_level(self, client, db):
        # After 3 sessions (30 XP), need 70 more to level up
        for _ in range(3):
            resp = client.post(
                "/api/sessions",
                data=json.dumps({}),
                content_type="application/json",
            )
        data = resp.get_json()
        assert data["xp_to_next_level"] == 70


class TestBadges:
    """Test badge awarding logic."""

    def test_first_pomodoro_badge(self, client, db):
        resp = client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = resp.get_json()
        assert "初めてのポモドーロ" in data["new_badges"]

    def test_five_completions_badge(self, client, db):
        for i in range(5):
            resp = client.post(
                "/api/sessions",
                data=json.dumps({}),
                content_type="application/json",
            )
        data = resp.get_json()
        assert "5回達成" in data["new_badges"]

    def test_ten_completions_badge(self, client, db):
        for i in range(10):
            resp = client.post(
                "/api/sessions",
                data=json.dumps({}),
                content_type="application/json",
            )
        data = resp.get_json()
        assert "10回達成" in data["new_badges"]

    def test_badge_not_awarded_twice(self, client, db):
        # First session
        resp1 = client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert "初めてのポモドーロ" in resp1.get_json()["new_badges"]

        # Second session
        resp2 = client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert "初めてのポモドーロ" not in resp2.get_json()["new_badges"]

    def test_three_day_streak_badge(self, client, db, app):
        """Test 3-day streak badge by inserting sessions on consecutive days."""
        with app.app_context():
            now = datetime.now(timezone.utc)
            for i in range(3):
                session = PomodoroSession(
                    duration_minutes=25,
                    completed_at=now - timedelta(days=i),
                )
                db.session.add(session)
            db.session.commit()

        # Trigger badge check via new session
        resp = client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = resp.get_json()
        # Should have the 3-day streak badge (3 pre-existing days + today's new one covers it)
        assert "3日連続" in data["new_badges"]


class TestGamificationEndpoint:
    """Test GET /api/gamification returns correct structure."""

    def test_gamification_structure(self, client, db):
        resp = client.get("/api/gamification")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "xp" in data
        assert "level" in data
        assert "xp_to_next_level" in data
        assert "badges" in data
        assert "streak" in data
        assert "weekly_sessions" in data
        assert "monthly_sessions" in data

    def test_gamification_badges_list(self, client, db):
        resp = client.get("/api/gamification")
        data = resp.get_json()
        assert isinstance(data["badges"], list)
        assert len(data["badges"]) == 6
        for badge in data["badges"]:
            assert "name" in badge
            assert "description" in badge
            assert "icon" in badge
            assert "earned" in badge

    def test_gamification_streak_structure(self, client, db):
        resp = client.get("/api/gamification")
        data = resp.get_json()
        assert "current_streak" in data["streak"]
        assert "best_streak" in data["streak"]

    def test_gamification_after_session(self, client, db):
        client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        resp = client.get("/api/gamification")
        data = resp.get_json()
        assert data["xp"] == 10
        assert data["level"] == 1


class TestStatsEndpoint:
    """Test GET /api/stats returns correct structure."""

    def test_stats_structure(self, client, db):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "weekly" in data
        assert "monthly" in data
        assert isinstance(data["weekly"], list)
        assert len(data["weekly"]) == 7
        assert "total_sessions" in data["monthly"]
        assert "average_duration" in data["monthly"]
        assert "completion_rate" in data["monthly"]

    def test_stats_weekly_day_format(self, client, db):
        resp = client.get("/api/stats")
        data = resp.get_json()
        for day in data["weekly"]:
            assert "date" in day
            assert "sessions" in day

    def test_stats_after_sessions(self, client, db):
        for _ in range(3):
            client.post(
                "/api/sessions",
                data=json.dumps({"duration_minutes": 25}),
                content_type="application/json",
            )
        resp = client.get("/api/stats")
        data = resp.get_json()
        # Today should have 3 sessions
        today_entry = data["weekly"][-1]
        assert today_entry["sessions"] == 3
        assert data["monthly"]["total_sessions"] == 3
        assert data["monthly"]["average_duration"] == 25.0


class TestStreakCalculation:
    """Test streak calculation logic."""

    def test_no_sessions_zero_streak(self, client, db):
        resp = client.get("/api/gamification")
        data = resp.get_json()
        assert data["streak"]["current_streak"] == 0
        assert data["streak"]["best_streak"] == 0

    def test_single_session_today(self, client, db):
        client.post(
            "/api/sessions",
            data=json.dumps({}),
            content_type="application/json",
        )
        resp = client.get("/api/gamification")
        data = resp.get_json()
        assert data["streak"]["current_streak"] == 1
        assert data["streak"]["best_streak"] == 1

    def test_streak_with_gap(self, client, db, app):
        """Sessions today and 3 days ago should give streak of 1."""
        with app.app_context():
            now = datetime.now(timezone.utc)
            # Session 3 days ago
            s = PomodoroSession(
                duration_minutes=25, completed_at=now - timedelta(days=3)
            )
            db.session.add(s)
            # Session today
            s2 = PomodoroSession(duration_minutes=25, completed_at=now)
            db.session.add(s2)
            db.session.commit()

        resp = client.get("/api/gamification")
        data = resp.get_json()
        assert data["streak"]["current_streak"] == 1
        assert data["streak"]["best_streak"] == 1


class TestListSessions:
    """Test GET /api/sessions."""

    def test_list_empty(self, client, db):
        resp = client.get("/api/sessions")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_returns_sessions_newest_first(self, client, db):
        client.post(
            "/api/sessions",
            data=json.dumps({"duration_minutes": 25}),
            content_type="application/json",
        )
        client.post(
            "/api/sessions",
            data=json.dumps({"duration_minutes": 50}),
            content_type="application/json",
        )
        resp = client.get("/api/sessions")
        data = resp.get_json()
        assert len(data) == 2
        # Newest first
        assert data[0]["duration_minutes"] == 50


class TestIndexPage:
    """Test GET / serves the template."""

    def test_index_returns_html(self, client, db):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"<!DOCTYPE html>" in resp.data or b"html" in resp.data
