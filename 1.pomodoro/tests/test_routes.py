import json


class TestIndex:
    """GET / のテスト"""

    def test_index_returns_200(self, client):
        """トップページが正常に返される"""
        response = client.get("/")
        assert response.status_code == 200


class TestCreateSession:
    """POST /api/session のテスト"""

    def test_create_session_returns_201(self, client):
        """セッション作成が 201 を返す"""
        response = client.post(
            "/api/session",
            data=json.dumps({"duration": 1500, "type": "work"}),
            content_type="application/json",
        )
        assert response.status_code == 201

    def test_create_session_returns_session_data(self, client):
        """セッション作成がセッションデータを返す"""
        response = client.post(
            "/api/session",
            data=json.dumps({"duration": 1500, "type": "work"}),
            content_type="application/json",
        )
        data = response.get_json()
        assert data["duration"] == 1500
        assert data["type"] == "work"
        assert data["completed"] is True

    def test_create_session_default_values(self, client):
        """デフォルト値でセッション作成"""
        response = client.post(
            "/api/session",
            data=json.dumps({}),
            content_type="application/json",
        )
        data = response.get_json()
        assert data["duration"] == 1500
        assert data["type"] == "work"

    def test_create_break_session(self, client):
        """break セッション作成"""
        response = client.post(
            "/api/session",
            data=json.dumps({"duration": 300, "type": "break"}),
            content_type="application/json",
        )
        data = response.get_json()
        assert data["type"] == "break"
        assert data["duration"] == 300


class TestTodayStats:
    """GET /api/stats/today のテスト"""

    def test_stats_returns_200(self, client):
        """統計取得が 200 を返す"""
        response = client.get("/api/stats/today")
        assert response.status_code == 200

    def test_stats_empty(self, client):
        """セッションがない場合の統計"""
        response = client.get("/api/stats/today")
        data = response.get_json()
        assert data["completed_sessions"] == 0
        assert data["total_focus_time"] == 0

    def test_stats_after_session(self, client):
        """セッション作成後の統計"""
        client.post(
            "/api/session",
            data=json.dumps({"duration": 1500, "type": "work"}),
            content_type="application/json",
        )
        response = client.get("/api/stats/today")
        data = response.get_json()
        assert data["completed_sessions"] == 1
        assert data["total_focus_time"] == 1500
