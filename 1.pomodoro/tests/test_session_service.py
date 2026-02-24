from unittest.mock import MagicMock
from services.session_service import SessionService


class TestCompleteSession:
    """SessionService.complete_session のテスト"""

    def test_complete_session_returns_dict(self):
        """セッション完了時に辞書が返される"""
        mock_repo = MagicMock()
        mock_session = MagicMock()
        mock_session.to_dict.return_value = {
            "id": 1,
            "started_at": "2026-01-01T00:00:00",
            "type": "work",
            "duration": 1500,
            "completed": True,
        }
        mock_repo.add_session.return_value = mock_session

        service = SessionService(mock_repo)
        result = service.complete_session(duration=1500, session_type="work")

        assert result["id"] == 1
        assert result["type"] == "work"
        assert result["duration"] == 1500
        assert result["completed"] is True
        mock_repo.add_session.assert_called_once_with(
            session_type="work", duration=1500, completed=True
        )

    def test_complete_session_default_type_is_work(self):
        """デフォルトのセッションタイプは work"""
        mock_repo = MagicMock()
        mock_session = MagicMock()
        mock_session.to_dict.return_value = {"type": "work"}
        mock_repo.add_session.return_value = mock_session

        service = SessionService(mock_repo)
        service.complete_session(duration=1500)

        mock_repo.add_session.assert_called_once_with(
            session_type="work", duration=1500, completed=True
        )

    def test_complete_session_break_type(self):
        """break タイプのセッション完了"""
        mock_repo = MagicMock()
        mock_session = MagicMock()
        mock_session.to_dict.return_value = {"type": "break"}
        mock_repo.add_session.return_value = mock_session

        service = SessionService(mock_repo)
        service.complete_session(duration=300, session_type="break")

        mock_repo.add_session.assert_called_once_with(
            session_type="break", duration=300, completed=True
        )


class TestGetTodayStats:
    """SessionService.get_today_stats のテスト"""

    def test_empty_sessions(self):
        """セッションがない場合は 0 を返す"""
        mock_repo = MagicMock()
        mock_repo.get_today_sessions.return_value = []

        service = SessionService(mock_repo)
        stats = service.get_today_stats()

        assert stats["completed_sessions"] == 0
        assert stats["total_focus_time"] == 0

    def test_multiple_work_sessions(self):
        """複数の work セッションの集計"""
        mock_repo = MagicMock()
        session1 = MagicMock(type="work", completed=True, duration=1500)
        session2 = MagicMock(type="work", completed=True, duration=1500)
        mock_repo.get_today_sessions.return_value = [session1, session2]

        service = SessionService(mock_repo)
        stats = service.get_today_stats()

        assert stats["completed_sessions"] == 2
        assert stats["total_focus_time"] == 3000

    def test_break_sessions_excluded_from_stats(self):
        """break セッションは集計から除外"""
        mock_repo = MagicMock()
        work = MagicMock(type="work", completed=True, duration=1500)
        brk = MagicMock(type="break", completed=True, duration=300)
        mock_repo.get_today_sessions.return_value = [work, brk]

        service = SessionService(mock_repo)
        stats = service.get_today_stats()

        assert stats["completed_sessions"] == 1
        assert stats["total_focus_time"] == 1500

    def test_incomplete_sessions_excluded(self):
        """未完了のセッションは集計から除外"""
        mock_repo = MagicMock()
        completed = MagicMock(type="work", completed=True, duration=1500)
        incomplete = MagicMock(type="work", completed=False, duration=1500)
        mock_repo.get_today_sessions.return_value = [completed, incomplete]

        service = SessionService(mock_repo)
        stats = service.get_today_stats()

        assert stats["completed_sessions"] == 1
        assert stats["total_focus_time"] == 1500
