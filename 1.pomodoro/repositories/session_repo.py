from datetime import datetime, timezone

from database import db
from models import Session


class SessionRepository:
    def add_session(self, duration: int) -> Session:
        session = Session(
            duration=duration,
            completed_at=datetime.now(timezone.utc),
        )
        db.session.add(session)
        db.session.commit()
        return session

    def get_today_sessions(self) -> list[Session]:
        today = datetime.now(timezone.utc).date()
        return Session.query.filter(
            db.func.date(Session.completed_at) == today
        ).all()
