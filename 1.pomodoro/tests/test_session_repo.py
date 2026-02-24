from repositories.session_repo import SessionRepository


class TestSessionRepository:
    """SessionRepository のテスト"""

    def test_add_session(self, app, db):
        with app.app_context():
            repo = SessionRepository()
            session = repo.add_session(session_type="work", duration=1500, completed=True)

            assert session.id is not None
            assert session.type == "work"
            assert session.duration == 1500
            assert session.completed is True

    def test_add_break_session(self, app, db):
        with app.app_context():
            repo = SessionRepository()
            session = repo.add_session(session_type="break", duration=300, completed=True)

            assert session.type == "break"
            assert session.duration == 300

    def test_get_today_sessions(self, app, db):
        with app.app_context():
            repo = SessionRepository()
            repo.add_session(session_type="work", duration=1500)
            repo.add_session(session_type="break", duration=300)

            sessions = repo.get_today_sessions()
            assert len(sessions) == 2
            assert sessions[0].type == "work"
            assert sessions[1].type == "break"

    def test_get_today_sessions_empty(self, app, db):
        with app.app_context():
            repo = SessionRepository()
            sessions = repo.get_today_sessions()
            assert sessions == []
