from datetime import datetime, timezone

from database import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer, nullable=False, default=25)
    completed_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "duration": self.duration,
            "completed_at": self.completed_at.isoformat(),
        }


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    work_duration = db.Column(db.Integer, nullable=False, default=25)
    break_duration = db.Column(db.Integer, nullable=False, default=5)

    def to_dict(self):
        return {
            "work_duration": self.work_duration,
            "break_duration": self.break_duration,
        }
