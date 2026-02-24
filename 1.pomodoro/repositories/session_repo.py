from datetime import datetime, timezone
from database import db
from models import Session


class SessionRepository:
    """DB アクセスの抽象化"""

    def add_session(self, session_type, duration, completed=True):
        """セッションを追加する"""
        session = Session(
            type=session_type,
            duration=duration,
            completed=completed,
        )
        db.session.add(session)
        db.session.commit()
        return session

    def get_today_sessions(self):
        """今日のセッション一覧を取得する"""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return Session.query.filter(Session.started_at >= today_start).all()
