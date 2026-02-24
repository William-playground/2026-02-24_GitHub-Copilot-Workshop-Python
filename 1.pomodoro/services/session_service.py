class SessionService:
    """ビジネスロジック（Flask 非依存）"""

    def __init__(self, repo):
        self.repo = repo

    def complete_session(self, duration, session_type="work"):
        """セッション完了を記録する"""
        session = self.repo.add_session(
            session_type=session_type,
            duration=duration,
            completed=True,
        )
        return session.to_dict()

    def get_today_stats(self):
        """今日の集計値を返す"""
        sessions = self.repo.get_today_sessions()
        work_sessions = [s for s in sessions if s.type == "work" and s.completed]
        total_focus_time = sum(s.duration for s in work_sessions)
        return {
            "completed_sessions": len(work_sessions),
            "total_focus_time": total_focus_time,
        }
