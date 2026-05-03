from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
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
    stop_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._led = StatusLed("gray")
        self._status_label = QLabel("Not recording")
        self._start_btn = QPushButton("Start Recording")
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setEnabled(False)

        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn.clicked.connect(self.stop_requested)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(self._led)
        layout.addWidget(self._status_label)
        layout.addStretch()
        layout.addWidget(self._start_btn)
        layout.addWidget(self._stop_btn)

    def _on_start(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Recording", "plc_recording.json", "JSON (*.json)"
        )
        if path:
            self.start_requested.emit(path)

    def set_recording(self) -> None:
        self._led.set_red()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def set_idle(self) -> None:
        self._led.set_gray()
        self._status_label.setText("Not recording")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def set_connected(self, connected: bool) -> None:
        self._start_btn.setEnabled(connected)

    def update_status(self, elapsed: float, remaining: float, samples: int) -> None:
        self._status_label.setText(
            f"Recording  {_fmt_duration(elapsed)} / 12:00:00  —  {samples:,} samples"
        )
