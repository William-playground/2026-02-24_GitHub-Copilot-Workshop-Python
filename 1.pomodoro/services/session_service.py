from repositories.session_repo import SessionRepository


class SessionService:
    def __init__(self, repo: SessionRepository | None = None):
        self.repo = repo or SessionRepository()

    def complete_session(self, duration: int) -> dict:
        session = self.repo.add_session(duration)
        return session.to_dict()

    def get_today_stats(self) -> dict:
        sessions = self.repo.get_today_sessions()
        total = len(sessions)
        total_minutes = sum(s.duration for s in sessions)
        return {
            "total_sessions": total,
            "total_minutes": total_minutes,
        }
