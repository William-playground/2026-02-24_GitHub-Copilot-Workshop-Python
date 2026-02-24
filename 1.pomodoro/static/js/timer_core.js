"use strict";

/**
 * PomodoroTimer — DOM に依存しない純粋なタイマー状態管理クラス
 *
 * 状態遷移:
 *   IDLE  --start()--> RUNNING --tick()x25min--> BREAK --tick()x5min--> IDLE
 *   RUNNING / BREAK --pause()--> PAUSED --pause()--> (元の状態)
 *   任意 --reset()--> IDLE
 */
class PomodoroTimer {
  /** タイマーの状態定数 */
  static State = Object.freeze({
    IDLE: "IDLE",
    RUNNING: "RUNNING",
    BREAK: "BREAK",
    PAUSED: "PAUSED",
  });

  /** デフォルト設定（秒単位） */
  static DEFAULTS = Object.freeze({
    WORK_DURATION: 25 * 60,
    BREAK_DURATION: 5 * 60,
  });

  /**
   * @param {object} [options]
   * @param {number} [options.workDuration]  作業時間（秒）デフォルト 25 分
   * @param {number} [options.breakDuration] 休憩時間（秒）デフォルト 5 分
   */
  constructor(options = {}) {
    this._workDuration =
      options.workDuration ?? PomodoroTimer.DEFAULTS.WORK_DURATION;
    this._breakDuration =
      options.breakDuration ?? PomodoroTimer.DEFAULTS.BREAK_DURATION;

    this._state = PomodoroTimer.State.IDLE;
    this._remaining = this._workDuration;
    this._previousState = null; // PAUSED 時の復帰先
  }

  /** 現在の状態スナップショットを返す */
  getState() {
    return {
      state: this._state,
      remaining: this._remaining,
      workDuration: this._workDuration,
      breakDuration: this._breakDuration,
    };
  }

  /**
   * タイマーを開始する。
   * IDLE 状態のときのみ RUNNING へ遷移する。
   */
  start() {
    if (this._state !== PomodoroTimer.State.IDLE) {
      return;
    }
    this._state = PomodoroTimer.State.RUNNING;
    this._remaining = this._workDuration;
  }

  /**
   * タイマーをリセットして IDLE に戻す。
   */
  reset() {
    this._state = PomodoroTimer.State.IDLE;
    this._remaining = this._workDuration;
    this._previousState = null;
  }

  /**
   * 一時停止 / 再開をトグルする。
   * RUNNING / BREAK → PAUSED、PAUSED → 元の状態
   */
  pause() {
    const { RUNNING, BREAK, PAUSED } = PomodoroTimer.State;

    if (this._state === RUNNING || this._state === BREAK) {
      this._previousState = this._state;
      this._state = PAUSED;
    } else if (this._state === PAUSED && this._previousState) {
      this._state = this._previousState;
      this._previousState = null;
    }
  }

  /**
   * 1 秒分タイマーを進める。
   * RUNNING 中に残り 0 になると BREAK へ自動遷移する。
   * BREAK 中に残り 0 になると IDLE へ戻る。
   */
  tick() {
    const { RUNNING, BREAK, IDLE } = PomodoroTimer.State;

    if (this._state === RUNNING) {
      this._remaining = Math.max(0, this._remaining - 1);
      if (this._remaining === 0) {
        this._state = BREAK;
        this._remaining = this._breakDuration;
      }
    } else if (this._state === BREAK) {
      this._remaining = Math.max(0, this._remaining - 1);
      if (this._remaining === 0) {
        this._state = IDLE;
        this._remaining = this._workDuration;
      }
    }
  }
}

/* ブラウザ / Node.js 両対応のエクスポート */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { PomodoroTimer };
}
