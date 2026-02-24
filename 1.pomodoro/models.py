from datetime import datetime, timezone

from database import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=False, default=25)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Session {self.id} duration={self.duration}>"
