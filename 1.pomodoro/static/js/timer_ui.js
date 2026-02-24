/**
 * Pomodoro Timer — timer_ui.js
 * DOM バインド・残り時間表示・API 呼び出し
 */
(function () {
  "use strict";

  // --- 定数 ---------------------------------------------------------------
  var WORK_MINUTES = 25;
  var BREAK_MINUTES = 5;
  var CIRCUMFERENCE = 2 * Math.PI * 95; // SVG r=95

  // --- DOM 要素 -----------------------------------------------------------
  var statusLabel = document.getElementById("statusLabel");
  var timerRing = document.getElementById("timerRing");
  var progressBar = document.getElementById("progressBar");
  var timeDisplay = document.getElementById("timeDisplay");
  var btnStart = document.getElementById("btnStart");
  var btnReset = document.getElementById("btnReset");
  var completedCount = document.getElementById("completedCount");
  var focusTime = document.getElementById("focusTime");

  // --- タイマー状態 -------------------------------------------------------
  var isRunning = false;
  var isBreak = false;
  var totalSeconds = WORK_MINUTES * 60;
  var remainingSeconds = totalSeconds;
  var intervalId = null;

  // --- ヘルパー関数 -------------------------------------------------------

  /** mm:ss 形式にフォーマット */
  function formatTime(sec) {
    var m = Math.floor(sec / 60);
    var s = sec % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  /** 集中時間を「◯時間◯分」「◯分」形式にフォーマット */
  function formatFocusTime(minutes) {
    if (minutes >= 60) {
      var h = Math.floor(minutes / 60);
      var m = minutes % 60;
      return m > 0 ? h + "時間" + m + "分" : h + "時間";
    }
    return minutes + "分";
  }

  /** プログレスバー更新 */
  function updateRing() {
    var progress = 1 - remainingSeconds / totalSeconds;
    progressBar.setAttribute(
      "stroke-dashoffset",
      CIRCUMFERENCE * (1 - progress)
    );
  }

  /** 時間表示更新 */
  function updateDisplay() {
    timeDisplay.textContent = formatTime(remainingSeconds);
    updateRing();
  }

  /** 進捗パネル更新 (API から取得) */
  function refreshProgress() {
    fetch("/api/status")
      .then(function (res) { return res.json(); })
      .then(function (data) {
        completedCount.textContent = String(data.completed);
        focusTime.textContent = formatFocusTime(data.total_focus_minutes);
      })
      .catch(function (err) { console.error("status fetch error:", err); });
  }

  /** 作業完了を API に送信 */
  function reportCompletion(minutes) {
    fetch("/api/complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ minutes: minutes }),
    })
      .then(function () { refreshProgress(); })
      .catch(function (err) { console.error("complete post error:", err); });
  }

  // --- タイマー制御 -------------------------------------------------------

  /** 1 秒ごとのティック */
  function tick() {
    if (remainingSeconds <= 0) {
      clearInterval(intervalId);
      intervalId = null;
      isRunning = false;

      if (!isBreak) {
        // 作業 → 休憩
        reportCompletion(WORK_MINUTES);
        startBreak();
      } else {
        // 休憩 → 作業に戻る
        switchToWork();
      }
      return;
    }
    remainingSeconds--;
    updateDisplay();
  }

  /** タイマー開始 */
  function startTimer() {
    if (isRunning) return;
    isRunning = true;
    btnStart.textContent = "停止";
    intervalId = setInterval(tick, 1000);
  }

  /** タイマー停止 */
  function stopTimer() {
    if (!isRunning) return;
    isRunning = false;
    btnStart.textContent = isBreak ? "休憩開始" : "開始";
    clearInterval(intervalId);
    intervalId = null;
  }

  /** 休憩モードへ切替 */
  function startBreak() {
    isBreak = true;
    totalSeconds = BREAK_MINUTES * 60;
    remainingSeconds = totalSeconds;
    statusLabel.textContent = "休憩中";
    timerRing.classList.add("timer-ring--break");
    btnStart.textContent = "休憩開始";
    updateDisplay();
    // 自動で休憩タイマー開始
    startTimer();
  }

  /** 作業モードへ切替 */
  function switchToWork() {
    isBreak = false;
    totalSeconds = WORK_MINUTES * 60;
    remainingSeconds = totalSeconds;
    statusLabel.textContent = "作業中";
    timerRing.classList.remove("timer-ring--break");
    btnStart.textContent = "開始";
    updateDisplay();
  }

  /** リセット */
  function resetTimer() {
    stopTimer();
    switchToWork();
  }

  // --- イベントバインド ---------------------------------------------------
  btnStart.addEventListener("click", function () {
    if (isRunning) {
      stopTimer();
    } else {
      startTimer();
    }
  });

  btnReset.addEventListener("click", resetTimer);

  // --- 初期化 -------------------------------------------------------------
  updateDisplay();
  refreshProgress();
})();
