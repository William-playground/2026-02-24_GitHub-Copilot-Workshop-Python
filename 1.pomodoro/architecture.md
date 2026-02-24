# ポモドーロタイマー Web アプリ アーキテクチャ案

## 技術スタック

| 用途 | 技術 |
|---|---|
| サーバー | Flask + Flask-SQLAlchemy |
| DB | SQLite |
| フロントエンド | Vanilla JS + CSS Variables |
| 円形プログレス | SVG `<circle>` + `stroke-dashoffset` |

---

## ディレクトリ構成

```
1.pomodoro/
├── app.py                          # create_app() ファクトリのみ（薄く保つ）
├── config.py                       # 環境別設定（本番 / テスト）
├── models.py                       # SQLAlchemy データモデル
├── database.py                     # DB 初期化・接続ユーティリティ
├── pomodoro.db                     # SQLite データベース（自動生成）
├── services/
│   └── session_service.py          # ビジネスロジック（Flask 非依存）
├── repositories/
│   └── session_repo.py             # DB アクセスの抽象化
├── static/
│   ├── css/
│   │   └── style.css               # UI スタイル（グラデーション・円形プログレス）
│   └── js/
│       ├── timer_core.js           # 純粋なタイマー状態管理（DOM 依存なし）
│       └── timer_ui.js             # DOM 操作・イベントバインド
├── templates/
│   └── index.html                  # メイン画面テンプレート
└── tests/
    ├── conftest.py                  # 共通 pytest フィクスチャ
    ├── test_session_service.py      # サービスレイヤーのユニットテスト
    ├── test_session_repo.py         # リポジトリのユニットテスト
    └── test_routes.py              # Flask ルートの統合テスト
```

---

## レイヤー構成と責務

### バックエンド

#### `app.py` — ルーティング

`create_app(config)` ファクトリパターンを採用し、環境に応じた設定を注入できるようにする。
ルートハンドラはサービスレイヤーを呼び出すだけに留め、ロジックを持たせない。

| エンドポイント | メソッド | 役割 |
|---|---|---|
| `/` | GET | メイン画面表示 |
| `/api/session` | POST | ポモドーロ完了を記録 |
| `/api/stats/today` | GET | 今日の完了数・集中時間を返す |
| `/api/settings` | GET / POST | タイマー設定の取得・保存 |

#### `services/session_service.py` — ビジネスロジック

Flask に依存せず、ビジネスルールのみを担当する。
依存性注入（DI）パターンで `SessionRepository` を受け取る。

```python
class SessionService:
    def __init__(self, repo: SessionRepository):
        self.repo = repo

    def complete_session(self, duration: int) -> dict: ...
    def get_today_stats(self) -> dict: ...
```

#### `repositories/session_repo.py` — DB アクセス抽象化

DB 操作をインターフェースとして切り出す。
テスト時はモックに差し替えることで DB なしでサービスのテストが可能。

#### `config.py` — 環境別設定

```python
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pomodoro.db'
    TESTING = False

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # インメモリDB
    TESTING = True
```

#### `models.py` — データモデル

```
Session テーブル
├── id          INTEGER PRIMARY KEY
├── started_at  DATETIME
├── type        TEXT  ('work' | 'break')
├── duration    INTEGER  # 秒
└── completed   BOOLEAN
```

---

### フロントエンド

#### `timer_core.js` — 純粋なタイマーロジック

DOM に一切依存しない状態管理クラス。Jest 等でブラウザなしにユニットテストできる。

```javascript
export class PomodoroTimer {
    // 状態: IDLE / RUNNING / BREAK / PAUSED
    start()     { ... }
    reset()     { ... }
    tick()      { ... }  // 1秒進める純粋関数
    getState()  { return { remaining, phase, ... } }
}
```

#### `timer_ui.js` — DOM 操作・イベントバインド

`PomodoroTimer` のインスタンスを受け取り、状態変化を画面に反映する。
開始・リセットボタンのイベント登録、SVG プログレスバーの更新、API 呼び出しを担当。

#### 円形プログレスバー

SVG の `<circle>` 要素に `stroke-dashoffset` を CSS アニメーションで操作して描画する。
外部 UI ライブラリは不要。

---

## タイマーの状態遷移

```
         開始ボタン
IDLE ──────────────→ RUNNING
 ↑                      │
 │  リセットボタン        │ タイマー満了
 │                      ↓
 ├──────────────── BREAK（休憩）
 │  リセットボタン        │ タイマー満了
 │                      │
 └────────────────────←─┘

RUNNING / BREAK 中に一時停止ボタン → PAUSED
PAUSED 中に再開ボタン → 元の状態に戻る
```

セッション完了（RUNNING → BREAK 遷移時）に `POST /api/session` を呼び出して記録する。

---

## テスト戦略

| テスト対象 | 手法 | ポイント |
|---|---|---|
| `session_service.py` | pytest + `MagicMock` | `repo` をモックに差し替え、Flask・DB 不要 |
| `session_repo.py` | pytest + `TestingConfig` | SQLite インメモリ DB を使用 |
| `test_routes.py` | Flask test client | `create_app(TestingConfig)` でインメモリ DB |
| `timer_core.js` | Jest | DOM 依存なしで純粋ロジックをテスト |

`tests/conftest.py` に共通フィクスチャ（アプリインスタンス・DBセットアップ）を集約し、テストコードの重複を排除する。
