"""Tests for the Pomodoro Timer Flask application."""
import sys
import os
import pytest

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_app_exists():
    """Test that the Flask app is created."""
    assert app is not None


def test_index_returns_200(client):
    """Test that the index page returns HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_title(client):
    """Test that the page contains the Japanese title."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "ポモドーロタイマー" in html


def test_index_contains_status_labels(client):
    """Test that the page contains work/break status labels."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "作業中" in html


def test_index_contains_buttons(client):
    """Test that the page contains start and reset buttons."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "開始" in html
    assert "リセット" in html


def test_index_contains_timer_display(client):
    """Test that the page contains the timer display element."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "25:00" in html


def test_index_contains_progress_section(client):
    """Test that the page contains the progress tracking section."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "今日の進捗" in html
    assert "完了" in html
    assert "集中時間" in html


def test_index_contains_svg_progress_ring(client):
    """Test that the page contains an SVG circular progress bar."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "<svg" in html
    assert "<circle" in html


def test_index_contains_canvas_for_particles(client):
    """Test that the page contains a canvas element for particle effects."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "<canvas" in html


def test_health_endpoint(client):
    """Test the health check endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_index_has_color_transition_logic(client):
    """Test that color transition logic is present in the page."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "interpolateColor" in html or "#6366f1" in html


def test_index_has_break_mode_label(client):
    """Test that break mode label exists in the JavaScript."""
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert "休憩中" in html
