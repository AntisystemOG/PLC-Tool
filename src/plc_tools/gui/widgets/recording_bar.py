from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from plc_tools.gui.widgets.status_led import StatusLed


def _fmt_duration(seconds: float) -> str:
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


class RecordingBar(QWidget):
    start_requested = Signal(str)
    stop_requested  = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rec_bar_root")
        self.setFixedHeight(42)
        self.setStyleSheet("""
            QWidget#rec_bar_root {
                background-color: #141720;
                border-top: 1px solid #2d3240;
            }
        """)

        self._led = StatusLed("gray")

        # Blinking "REC" label — only visible while recording
        self._rec_lbl = QLabel("● REC")
        self._rec_lbl.setStyleSheet(
            "QLabel { color: #e63946; font-size: 11px; font-weight: bold; letter-spacing: 1px; }"
        )
        self._rec_lbl.setVisible(False)

        self._status_label = QLabel("Not recording")
        self._status_label.setStyleSheet(
            "QLabel { color: #8b95a5; font-size: 12px; }"
        )

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(16)
        sep.setStyleSheet("QFrame { color: #383e50; }")

        self._start_btn = QPushButton("▶  Start Recording")
        self._start_btn.setObjectName("record_start_btn")

        self._stop_btn = QPushButton("■  Stop")
        self._stop_btn.setObjectName("record_stop_btn")
        self._stop_btn.setEnabled(False)

        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn.clicked.connect(self.stop_requested)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)
        layout.addWidget(self._led)
        layout.addWidget(self._rec_lbl)
        layout.addWidget(self._status_label)
        layout.addStretch()
        layout.addWidget(sep)
        layout.addWidget(self._start_btn)
        layout.addWidget(self._stop_btn)

        # Blink timer — toggles rec label visibility every 600 ms
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(600)
        self._blink_timer.timeout.connect(self._blink_tick)
        self._blink_state = True

    # ── Blink ─────────────────────────────────────────────────────────────────

    def _blink_tick(self) -> None:
        self._blink_state = not self._blink_state
        self._rec_lbl.setVisible(self._blink_state)

    # ── Slot ──────────────────────────────────────────────────────────────────

    def _on_start(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Recording", "plc_recording.json", "JSON (*.json)"
        )
        if path:
            self.start_requested.emit(path)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_recording(self) -> None:
        self._led.set_red()
        self._rec_lbl.setVisible(True)
        self._blink_state = True
        self._blink_timer.start()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def set_idle(self) -> None:
        self._blink_timer.stop()
        self._led.set_gray()
        self._rec_lbl.setVisible(False)
        self._status_label.setText("Not recording")
        self._status_label.setStyleSheet(
            "QLabel { color: #8b95a5; font-size: 12px; }"
        )
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def set_connected(self, connected: bool) -> None:
        self._start_btn.setEnabled(connected)

    def update_status(self, elapsed: float, remaining: float, samples: int) -> None:
        elapsed_str = _fmt_duration(elapsed)
        self._status_label.setText(
            f"{elapsed_str}  elapsed    {samples:,} samples"
        )
        self._status_label.setStyleSheet(
            "QLabel { color: #c0c4d0; font-size: 12px; font-family: Consolas, monospace; }"
        )
