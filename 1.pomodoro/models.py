from datetime import datetime, timezone
from database import db


class Session(db.Model):
    """ポモドーロセッションモデル"""
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    type = db.Column(db.String(10), nullable=False, default="work")  # 'work' | 'break'
    duration = db.Column(db.Integer, nullable=False)  # 秒
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "type": self.type,
            "duration": self.duration,
            "completed": self.completed,
        }

    def __repr__(self):
        return f"<Session id={self.id} type={self.type} completed={self.completed}>"
