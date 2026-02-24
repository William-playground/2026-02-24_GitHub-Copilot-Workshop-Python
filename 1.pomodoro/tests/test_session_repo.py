from repositories.session_repo import SessionRepository
from models import Session


class TestAddSession:
    """SessionRepository.add_session のテスト"""

    def test_add_work_session(self, app, db):
        """work セッションを追加できる"""
        with app.app_context():
            repo = SessionRepository()
            session = repo.add_session(session_type="work", duration=1500)

            assert session.id is not None
            assert session.type == "work"
            assert session.duration == 1500
            assert session.completed is True

    def test_add_break_session(self, app, db):
        """break セッションを追加できる"""
        with app.app_context():
            repo = SessionRepository()
            session = repo.add_session(session_type="break", duration=300)

            assert session.type == "break"
            assert session.duration == 300

    def test_add_session_persists_to_db(self, app, db):
        """セッションが DB に永続化される"""
        with app.app_context():
            repo = SessionRepository()
            repo.add_session(session_type="work", duration=1500)

            sessions = Session.query.all()
            assert len(sessions) == 1
            assert sessions[0].type == "work"


class TestGetTodaySessions:
    """SessionRepository.get_today_sessions のテスト"""

    def test_returns_today_sessions(self, app, db):
        """今日のセッションを取得する"""
        with app.app_context():
            repo = SessionRepository()
            repo.add_session(session_type="work", duration=1500)
            repo.add_session(session_type="break", duration=300)

            sessions = repo.get_today_sessions()
            assert len(sessions) == 2

    def test_returns_empty_when_no_sessions(self, app, db):
        """セッションがない場合は空リストを返す"""
        with app.app_context():
            repo = SessionRepository()
            sessions = repo.get_today_sessions()
            assert sessions == []
