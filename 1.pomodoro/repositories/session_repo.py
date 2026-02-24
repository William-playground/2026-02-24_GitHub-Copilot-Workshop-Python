from datetime import date, datetime, timezone

from database import db
from models import Session


class SessionRepository:
    """ポモドーロセッションの DB アクセス層"""

    def add_session(self, session_type="work", duration=1500, completed=True):
        """セッションを DB に追加する

        Args:
            session_type: セッション種別 ('work' | 'break')
            duration: セッション時間（秒）
            completed: 完了フラグ

        Returns:
            追加された Session オブジェクト
        """
        session = Session(
            type=session_type,
            duration=duration,
            completed=completed,
            started_at=datetime.now(timezone.utc),
        )
        db.session.add(session)
        db.session.commit()
        return session

    def get_today_sessions(self):
        """今日のセッション一覧を取得する

        Returns:
            今日のセッションのリスト
        """
        today_start = datetime.combine(date.today(), datetime.min.time(), tzinfo=timezone.utc)
        return (
            Session.query
            .filter(Session.started_at >= today_start)
            .order_by(Session.started_at)
            .all()
        )
