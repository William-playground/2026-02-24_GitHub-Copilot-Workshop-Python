# ポモドーロタイマー 実装機能一覧

## バックエンド

### アプリケーション基盤
- [ ] `config.py` — 本番用・テスト用の設定クラス（`Config` / `TestingConfig`）
- [ ] `database.py` — SQLAlchemy インスタンスの初期化・DB 接続ユーティリティ
- [ ] `models.py` — `Session` テーブル（id, started_at, type, duration, completed）
- [ ] `app.py` — `create_app()` ファクトリパターン・ルート定義

### API エンドポイント
- [ ] `GET /` — メイン画面（index.html）の返却
- [ ] `POST /api/session` — ポモドーロ完了を DB に記録
- [ ] `GET /api/stats/today` — 今日の完了数・集中時間の集計・返却
- [ ] `GET /api/settings` — タイマー設定（作業時間・休憩時間）の取得
- [ ] `POST /api/settings` — タイマー設定（作業時間・休憩時間）の保存

### ビジネスロジック / DB アクセス
- [ ] `services/session_service.py` — `complete_session()` / `get_today_stats()` の実装
- [ ] `repositories/session_repo.py` — DB アクセスの抽象化（DI 対応）

---

## フロントエンド

### タイマーロジック（`timer_core.js`）
- [ ] タイマー状態管理（IDLE / RUNNING / BREAK / PAUSED）
- [ ] `start()` / `reset()` / `tick()` / `getState()` の実装
- [ ] RUNNING → BREAK の自動遷移（タイマー満了検知）
- [ ] PAUSED 状態のトグル（一時停止 / 再開）

### UI / DOM 操作（`timer_ui.js`）
- [ ] 残り時間の表示更新（`MM:SS` フォーマット）
- [ ] 開始・リセットボタンのイベントバインド
- [ ] フェーズラベルの表示切り替え（「作業中」/「休憩中」）
- [ ] セッション完了時に `POST /api/session` を呼び出し
- [ ] ページ表示時に `GET /api/stats/today` を呼び出して進捗を更新

### 円形プログレスバー（`index.html` + `style.css`）
- [ ] SVG `<circle>` による円形プログレスの描画
- [ ] `stroke-dashoffset` のアニメーション更新（残り時間に連動）

### 今日の進捗パネル
- [ ] 「完了セッション数」の表示
- [ ] 「集中時間（時間・分）」の表示

---

## テスト

- [ ] `tests/conftest.py` — アプリインスタンス・インメモリ DB の共通フィクスチャ
- [ ] `tests/test_session_service.py` — `MagicMock` を使ったサービスのユニットテスト
- [ ] `tests/test_session_repo.py` — リポジトリのユニットテスト
- [ ] `tests/test_routes.py` — Flask test client を使った統合テスト
