"""Tests for the Pomodoro Timer Flask app."""

import pytest
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app as flask_app


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config["TESTING"] = True
    # Reset settings to defaults before each test
    from app import settings

    settings.update(
        {
            "work_duration": 25,
            "break_duration": 5,
            "theme": "dark",
            "sound_start": True,
            "sound_end": True,
            "sound_tick": False,
        }
    )
    yield flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


class TestIndexPage:
    """Tests for the main page."""

    def test_get_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_get_index_contains_timer_display(self, client):
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "timer-display" in html

    def test_get_index_contains_controls(self, client):
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "btn-start" in html
        assert "btn-pause" in html
        assert "btn-reset" in html

    def test_get_index_contains_settings_panel(self, client):
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "settings-panel" in html


class TestGetSettings:
    """Tests for GET /api/settings."""

    def test_returns_200(self, client):
        response = client.get("/api/settings")
        assert response.status_code == 200

    def test_returns_json(self, client):
        response = client.get("/api/settings")
        assert response.content_type == "application/json"

    def test_returns_default_settings(self, client):
        response = client.get("/api/settings")
        data = response.get_json()
        assert data["work_duration"] == 25
        assert data["break_duration"] == 5
        assert data["theme"] == "dark"
        assert data["sound_start"] is True
        assert data["sound_end"] is True
        assert data["sound_tick"] is False


class TestUpdateSettings:
    """Tests for POST /api/settings."""

    def test_update_all_settings(self, client):
        response = client.post(
            "/api/settings",
            json={
                "work_duration": 45,
                "break_duration": 15,
                "theme": "light",
                "sound_start": False,
                "sound_end": False,
                "sound_tick": True,
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["work_duration"] == 45
        assert data["break_duration"] == 15
        assert data["theme"] == "light"
        assert data["sound_start"] is False
        assert data["sound_end"] is False
        assert data["sound_tick"] is True

    def test_partial_update_work_duration(self, client):
        response = client.post("/api/settings", json={"work_duration": 35})
        assert response.status_code == 200
        data = response.get_json()
        assert data["work_duration"] == 35
        # Other settings remain at defaults
        assert data["break_duration"] == 5
        assert data["theme"] == "dark"

    def test_partial_update_theme(self, client):
        response = client.post("/api/settings", json={"theme": "focus"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["theme"] == "focus"
        assert data["work_duration"] == 25

    def test_partial_update_sound(self, client):
        response = client.post("/api/settings", json={"sound_tick": True})
        assert response.status_code == 200
        data = response.get_json()
        assert data["sound_tick"] is True
        assert data["sound_start"] is True  # unchanged

    def test_invalid_work_duration_returns_400(self, client):
        response = client.post("/api/settings", json={"work_duration": 20})
        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data

    def test_invalid_break_duration_returns_400(self, client):
        response = client.post("/api/settings", json={"break_duration": 7})
        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data

    def test_invalid_theme_returns_400(self, client):
        response = client.post("/api/settings", json={"theme": "rainbow"})
        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data

    def test_invalid_sound_type_returns_400(self, client):
        response = client.post("/api/settings", json={"sound_start": "yes"})
        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data

    def test_non_json_body_returns_error(self, client):
        response = client.post(
            "/api/settings",
            data="not json",
            content_type="text/plain",
        )
        assert response.status_code in (400, 415)

    def test_settings_persist_across_requests(self, client):
        client.post("/api/settings", json={"work_duration": 15})
        response = client.get("/api/settings")
        data = response.get_json()
        assert data["work_duration"] == 15
