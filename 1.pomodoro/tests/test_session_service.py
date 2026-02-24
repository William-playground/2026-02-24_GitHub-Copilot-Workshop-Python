from datetime import datetime, timezone
from unittest.mock import MagicMock

from models import Session
from services.session_service import SessionService


class TestSessionService:
    """SessionService のテスト"""

    def test_complete_session(self, app, db):
        with app.app_context():
            service = SessionService()
            session = service.complete_session(session_type="work", duration=1500)

            assert session.type == "work"
            assert session.duration == 1500
            assert session.completed is True

    def test_get_today_stats(self, app, db):
        with app.app_context():
            service = SessionService()
            service.complete_session(session_type="work", duration=1500)
            service.complete_session(session_type="break", duration=300)
            service.complete_session(session_type="work", duration=1500)

            stats = service.get_today_stats()

            assert stats["total_sessions"] == 2
            assert stats["total_minutes"] == 50
            assert len(stats["sessions"]) == 3

    def test_get_today_stats_empty(self, app, db):
        with app.app_context():
            service = SessionService()
            stats = service.get_today_stats()

            assert stats["total_sessions"] == 0
            assert stats["total_minutes"] == 0
            assert stats["sessions"] == []

    def test_complete_session_with_mock_repo(self):
        """MagicMock でリポジトリを差し替えたテスト"""
        mock_repo = MagicMock()
        mock_session = Session(id=1, type="work", duration=1500, completed=True)
        mock_repo.add_session.return_value = mock_session

        service = SessionService(repo=mock_repo)
        result = service.complete_session(session_type="work", duration=1500)

        mock_repo.add_session.assert_called_once_with(
            session_type="work", duration=1500, completed=True
        )
        assert result.type == "work"

    def test_get_today_stats_with_mock_repo(self):
        """MagicMock で統計テスト"""
        now = datetime.now(timezone.utc)
        mock_repo = MagicMock()
        mock_repo.get_today_sessions.return_value = [
            Session(id=1, type="work", duration=1500, completed=True, started_at=now),
            Session(id=2, type="break", duration=300, completed=True, started_at=now),
        ]

        service = SessionService(repo=mock_repo)
        stats = service.get_today_stats()

        assert stats["total_sessions"] == 1
        assert stats["total_minutes"] == 25
