# ポモドーロタイマー 段階的実装計画

## Phase 1 — バックエンド基盤（依存なし・最小構成）

**目標:** Flask が起動し、トップページが返せる状態にする

- [ ] `config.py` — `Config` / `TestingConfig` クラス
- [ ] `database.py` — SQLAlchemy インスタンス初期化
- [ ] `models.py` — `Session` モデル定義
- [ ] `app.py` — `create_app()` ファクトリ + `GET /` ルート
- [ ] `templates/index.html` — 最小限の骨格 HTML（スタイルなし）

**完了の確認:** `flask run` でトップページが表示される

---

## Phase 2 — DB アクセス層 + ビジネスロジック層

**目標:** ロジックを独立したモジュールに分離し、テスト可能にする

- [ ] `repositories/session_repo.py` — `SessionRepository`（`add_session` / `get_today_sessions`）
- [ ] `services/session_service.py` — `SessionService`（`complete_session` / `get_today_stats`）

**完了の確認:** Python REPL でサービスを単体で呼び出せる

---

## Phase 3 — REST API 実装

**目標:** フロントからデータを記録・取得できる API を揃える

- [ ] `POST /api/session` — セッション完了の記録
- [ ] `GET /api/stats/today` — 今日の集計値を返す
- [ ] `GET|POST /api/settings` — 設定の取得・保存

**完了の確認:** `curl` や HTTPie で各エンドポイントが正常応答する

---

## Phase 4 — フロントエンド タイマーロジック

**目標:** DOM に依存しない純粋なタイマー状態管理を作る

- [ ] `static/js/timer_core.js` — `PomodoroTimer` クラス
  - 状態: `IDLE / RUNNING / BREAK / PAUSED`
  - `start()` / `reset()` / `tick()` / `getState()`
  - RUNNING → BREAK 自動遷移・PAUSED トグル

**完了の確認:** ブラウザコンソールで `new PomodoroTimer()` を操作できる

---

## Phase 5 — UI 実装（デザインの再現）

**目標:** 設計画像のデザインを忠実に実装する

- [ ] `static/css/style.css` — グラデーション背景・ウィンドウ風カード・CSS Variables
- [ ] `templates/index.html` — SVG 円形プログレスバー・ボタン・進捗パネル
- [ ] `static/js/timer_ui.js` — DOM バインド・残り時間表示・API 呼び出し

**完了の確認:** ブラウザで開始 → カウントダウン → 休憩遷移が動作する

---

## Phase 6 — テスト整備

**目標:** 各レイヤーを自動テストでカバーする

- [ ] `tests/conftest.py` — 共通フィクスチャ（インメモリ DB・テスト用アプリ）
- [ ] `tests/test_session_service.py` — `MagicMock` でリポジトリを差し替え
- [ ] `tests/test_session_repo.py` — インメモリ DB でリポジトリをテスト
- [ ] `tests/test_routes.py` — Flask test client で API を統合テスト

---

## 実装順序の補足

```
Phase 1 → Phase 2 → Phase 3  ← バックエンドを先に固める
                ↓
           Phase 4            ← フロントの純粋ロジックを独立して作る
                ↓
           Phase 5            ← UI は API と timer_core.js が揃ってから
                ↓
           Phase 6            ← 各レイヤー完成後に並行で書ける
```

> **Note:** Phase 2 と Phase 4 は互いに独立しているため、並行作業も可能。
