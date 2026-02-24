from repositories.session_repo import SessionRepository


class SessionService:
    """ポモドーロセッションのビジネスロジック層"""

    def __init__(self, repo=None):
        self.repo = repo or SessionRepository()

    def complete_session(self, session_type="work", duration=1500):
        """セッション完了を記録する

        Args:
            session_type: セッション種別 ('work' | 'break')
            duration: セッション時間（秒）

        Returns:
            記録された Session オブジェクト
        """
        return self.repo.add_session(
            session_type=session_type,
            duration=duration,
            completed=True,
        )

    def get_today_stats(self):
        """今日の統計情報を返す

        Returns:
            dict: {
                "total_sessions": 完了ワークセッション数,
                "total_minutes": 合計集中時間（分）,
                "sessions": セッション一覧（dict のリスト）
            }
        """
        sessions = self.repo.get_today_sessions()
        work_sessions = [s for s in sessions if s.type == "work" and s.completed]
        total_seconds = sum(s.duration for s in work_sessions)

        return {
            "total_sessions": len(work_sessions),
            "total_minutes": total_seconds // 60,
            "sessions": [s.to_dict() for s in sessions],
        }
