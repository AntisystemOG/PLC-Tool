from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from .status_led import StatusLed


class ConnectionBar(QWidget):
    disconnect_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._led = StatusLed("gray")
        self._status_label = QLabel("Not connected")
        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setEnabled(False)
        self._disconnect_btn.clicked.connect(self.disconnect_requested)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(self._led)
        layout.addWidget(self._status_label)
        layout.addStretch()
        layout.addWidget(self._disconnect_btn)

    def set_connected(self, ip: str, name: str) -> None:
        self._led.set_green()
        self._status_label.setText(f"Connected: {name} ({ip})")
        self._disconnect_btn.setEnabled(True)

    def set_disconnected(self) -> None:
        self._led.set_gray()
        self._status_label.setText("Not connected")
        self._disconnect_btn.setEnabled(False)

    def set_connecting(self, ip: str) -> None:
        self._led.set_yellow()
        self._status_label.setText(f"Connecting to {ip}…")
        self._disconnect_btn.setEnabled(False)

    def set_error(self, msg: str) -> None:
        self._led.set_red()
        self._status_label.setText(f"Error: {msg}")
        self._disconnect_btn.setEnabled(False)
