import json


class TestPostSession:
    def test_create_session(self, client, db):
        resp = client.post(
            "/api/session",
            data=json.dumps({"duration": 25}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["duration"] == 25
        assert "id" in data
        assert "completed_at" in data

    def test_create_session_default_duration(self, client, db):
        resp = client.post(
            "/api/session",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        assert resp.get_json()["duration"] == 25

    def test_create_session_invalid_duration(self, client, db):
        resp = client.post(
            "/api/session",
            data=json.dumps({"duration": -1}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_create_session_non_integer_duration(self, client, db):
        resp = client.post(
            "/api/session",
            data=json.dumps({"duration": "bad"}),
            content_type="application/json",
        )
        assert resp.status_code == 400


class TestStatsToday:
    def test_empty_stats(self, client, db):
        resp = client.get("/api/stats/today")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_sessions"] == 0
        assert data["total_minutes"] == 0

    def test_stats_after_sessions(self, client, db):
        client.post(
            "/api/session",
            data=json.dumps({"duration": 25}),
            content_type="application/json",
        )
        client.post(
            "/api/session",
            data=json.dumps({"duration": 15}),
            content_type="application/json",
        )
        resp = client.get("/api/stats/today")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total_sessions"] == 2
        assert data["total_minutes"] == 40


class TestSettings:
    def test_get_default_settings(self, client, db):
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["work_duration"] == 25
        assert data["break_duration"] == 5

    def test_update_settings(self, client, db):
        resp = client.post(
            "/api/settings",
            data=json.dumps({"work_duration": 30, "break_duration": 10}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["work_duration"] == 30
        assert data["break_duration"] == 10

    def test_get_updated_settings(self, client, db):
        client.post(
            "/api/settings",
            data=json.dumps({"work_duration": 45, "break_duration": 15}),
            content_type="application/json",
        )
        resp = client.get("/api/settings")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["work_duration"] == 45
        assert data["break_duration"] == 15

    def test_update_settings_invalid(self, client, db):
        resp = client.post(
            "/api/settings",
            data=json.dumps({"work_duration": -5}),
            content_type="application/json",
        )
        assert resp.status_code == 400
