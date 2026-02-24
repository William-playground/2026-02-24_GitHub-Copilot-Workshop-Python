/* ===== Pomodoro Timer ===== */

const State = Object.freeze({
    IDLE: "idle",
    RUNNING: "running",
    PAUSED: "paused",
    BREAK: "break",
});

class PomodoroTimer {
    constructor() {
        // DOM references
        this.display = document.getElementById("timer-display");
        this.modeLabel = document.getElementById("mode-label");
        this.btnStart = document.getElementById("btn-start");
        this.btnPause = document.getElementById("btn-pause");
        this.btnReset = document.getElementById("btn-reset");
        this.settingsToggle = document.getElementById("settings-toggle");
        this.settingsClose = document.getElementById("settings-close");
        this.settingsPanel = document.getElementById("settings-panel");
        this.settingsOverlay = document.getElementById("settings-overlay");

        // Timer state
        this.state = State.IDLE;
        this.intervalId = null;
        this.remainingSeconds = 0;
        this.isBreak = false;

        // Settings (defaults — overwritten by server on load)
        this.settings = {
            work_duration: 25,
            break_duration: 5,
            theme: "dark",
            sound_start: true,
            sound_end: true,
            sound_tick: false,
        };

        // Audio context (lazy init)
        this.audioCtx = null;

        this._bindEvents();
        this._loadSettings();
    }

    /* ---------- Event binding ---------- */

    _bindEvents() {
        this.btnStart.addEventListener("click", () => this.start());
        this.btnPause.addEventListener("click", () => this.pause());
        this.btnReset.addEventListener("click", () => this.reset());

        this.settingsToggle.addEventListener("click", () => this._openSettings());
        this.settingsClose.addEventListener("click", () => this._closeSettings());
        this.settingsOverlay.addEventListener("click", () => this._closeSettings());

        // Settings change handlers
        document.querySelectorAll('input[name="work_duration"]').forEach((el) =>
            el.addEventListener("change", (e) => this._onSettingChange("work_duration", Number(e.target.value)))
        );
        document.querySelectorAll('input[name="break_duration"]').forEach((el) =>
            el.addEventListener("change", (e) => this._onSettingChange("break_duration", Number(e.target.value)))
        );
        document.querySelectorAll('input[name="theme"]').forEach((el) =>
            el.addEventListener("change", (e) => this._onSettingChange("theme", e.target.value))
        );

        document.getElementById("sound_start").addEventListener("change", (e) =>
            this._onSettingChange("sound_start", e.target.checked)
        );
        document.getElementById("sound_end").addEventListener("change", (e) =>
            this._onSettingChange("sound_end", e.target.checked)
        );
        document.getElementById("sound_tick").addEventListener("change", (e) =>
            this._onSettingChange("sound_tick", e.target.checked)
        );
    }

    /* ---------- Timer controls ---------- */

    start() {
        if (this.state === State.RUNNING) return;

        if (this.state === State.IDLE) {
            const minutes = this.isBreak ? this.settings.break_duration : this.settings.work_duration;
            this.remainingSeconds = minutes * 60;
        }

        this.state = this.isBreak ? State.BREAK : State.RUNNING;
        this._updateButtons();
        this._updateModeLabel();

        if (this.settings.sound_start) {
            this._playBeep(660, 0.15);
        }

        this.intervalId = setInterval(() => this.tick(), 1000);
    }

    pause() {
        if (this.state !== State.RUNNING && this.state !== State.BREAK) return;

        clearInterval(this.intervalId);
        this.intervalId = null;
        this.state = State.PAUSED;
        this._updateButtons();
    }

    reset() {
        clearInterval(this.intervalId);
        this.intervalId = null;
        this.state = State.IDLE;
        this.isBreak = false;
        this.remainingSeconds = this.settings.work_duration * 60;
        this._updateDisplay();
        this._updateButtons();
        this._updateModeLabel();
    }

    tick() {
        if (this.remainingSeconds <= 0) {
            clearInterval(this.intervalId);
            this.intervalId = null;

            if (this.settings.sound_end) {
                this._playBeep(880, 0.3);
                setTimeout(() => this._playBeep(880, 0.3), 350);
            }

            // Switch between work and break
            this.isBreak = !this.isBreak;
            this.state = State.IDLE;
            this.start();
            return;
        }

        this.remainingSeconds--;
        this._updateDisplay();

        if (this.settings.sound_tick && this.remainingSeconds > 0) {
            this._playBeep(440, 0.03);
        }
    }

    /* ---------- Display helpers ---------- */

    _updateDisplay() {
        const mins = Math.floor(this.remainingSeconds / 60);
        const secs = this.remainingSeconds % 60;
        this.display.textContent = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }

    _updateButtons() {
        const isRunning = this.state === State.RUNNING || this.state === State.BREAK;
        this.btnStart.disabled = isRunning;
        this.btnPause.disabled = !isRunning;
    }

    _updateModeLabel() {
        if (this.isBreak) {
            this.modeLabel.textContent = "休憩中";
        } else {
            this.modeLabel.textContent = "作業中";
        }
    }

    /* ---------- Settings ---------- */

    async _loadSettings() {
        try {
            const res = await fetch("/api/settings");
            if (res.ok) {
                const data = await res.json();
                this.settings = data;
                this._applySettingsToUI();
                // Set initial display
                if (this.state === State.IDLE) {
                    this.remainingSeconds = this.settings.work_duration * 60;
                    this._updateDisplay();
                }
            }
        } catch (err) {
            console.error("Failed to load settings:", err);
        }
    }

    async _saveSettings(partial) {
        try {
            const res = await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(partial),
            });
            if (res.ok) {
                const data = await res.json();
                this.settings = data;
            }
        } catch (err) {
            console.error("Failed to save settings:", err);
        }
    }

    _applySettingsToUI() {
        // Theme
        document.body.setAttribute("data-theme", this.settings.theme);

        // Radio buttons
        const workRadio = document.querySelector(`input[name="work_duration"][value="${this.settings.work_duration}"]`);
        if (workRadio) workRadio.checked = true;

        const breakRadio = document.querySelector(`input[name="break_duration"][value="${this.settings.break_duration}"]`);
        if (breakRadio) breakRadio.checked = true;

        const themeRadio = document.querySelector(`input[name="theme"][value="${this.settings.theme}"]`);
        if (themeRadio) themeRadio.checked = true;

        // Checkboxes
        document.getElementById("sound_start").checked = this.settings.sound_start;
        document.getElementById("sound_end").checked = this.settings.sound_end;
        document.getElementById("sound_tick").checked = this.settings.sound_tick;
    }

    _onSettingChange(key, value) {
        this.settings[key] = value;
        this._saveSettings({ [key]: value });

        if (key === "theme") {
            document.body.setAttribute("data-theme", value);
        }

        // If timer is idle, update duration display
        if (this.state === State.IDLE) {
            if (key === "work_duration" && !this.isBreak) {
                this.remainingSeconds = value * 60;
                this._updateDisplay();
            }
            if (key === "break_duration" && this.isBreak) {
                this.remainingSeconds = value * 60;
                this._updateDisplay();
            }
        }
    }

    _openSettings() {
        this.settingsPanel.classList.add("open");
        this.settingsPanel.setAttribute("aria-hidden", "false");
    }

    _closeSettings() {
        this.settingsPanel.classList.remove("open");
        this.settingsPanel.setAttribute("aria-hidden", "true");
    }

    /* ---------- Sound (Web Audio API) ---------- */

    _getAudioContext() {
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        return this.audioCtx;
    }

    _playBeep(frequency, duration) {
        try {
            const ctx = this._getAudioContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "sine";
            osc.frequency.setValueAtTime(frequency, ctx.currentTime);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);

            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + duration);
        } catch (err) {
            // Audio not available — silently ignore
        }
    }
}

/* ---------- Init ---------- */
document.addEventListener("DOMContentLoaded", () => {
    new PomodoroTimer();
});
