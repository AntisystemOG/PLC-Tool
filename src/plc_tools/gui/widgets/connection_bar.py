from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from .status_led import StatusLed

_BADGE_BASE = """
    QLabel {
        font-size: 10px;
        font-weight: bold;
        letter-spacing: 1.8px;
        padding: 2px 8px;
        border-radius: 3px;
    }
"""


class ConnectionBar(QWidget):
    disconnect_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("conn_bar_root")
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QWidget#conn_bar_root {
                background-color: #141720;
                border-bottom: 1px solid #2d3240;
            }
        """)

        self._led = StatusLed("gray")

        self._badge = QLabel("NOT CONNECTED")
        self._badge.setStyleSheet(
            _BADGE_BASE + "QLabel { background-color: #252930; color: #6b7280; }"
        )

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(18)
        sep.setStyleSheet("QFrame { color: #383e50; }")

        self._name_lbl = QLabel("")
        self._name_lbl.setStyleSheet(
            "QLabel { color: #e8eaf0; font-size: 14px; font-weight: bold; }"
        )

        self._detail_lbl = QLabel("")
        self._detail_lbl.setStyleSheet(
            "QLabel { color: #8b95a5; font-size: 12px; }"
        )

        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setObjectName("disconnect_btn")
        self._disconnect_btn.setFixedWidth(110)
        self._disconnect_btn.setEnabled(False)
        self._disconnect_btn.clicked.connect(self.disconnect_requested)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)
        layout.addWidget(self._led)
        layout.addWidget(self._badge)
        layout.addWidget(sep)
        layout.addWidget(self._name_lbl)
        layout.addWidget(self._detail_lbl)
        layout.addStretch()
        layout.addWidget(self._disconnect_btn)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_connected(self, ip: str, name: str) -> None:
        self._led.set_green()
        self._badge.setText("CONNECTED")
        self._badge.setStyleSheet(
            _BADGE_BASE + "QLabel { background-color: #0f3020; color: #3dd68c; }"
        )
        self._name_lbl.setText(name)
        self._detail_lbl.setText(f"   {ip}")
        self._disconnect_btn.setEnabled(True)

    def set_disconnected(self) -> None:
        self._led.set_gray()
        self._badge.setText("NOT CONNECTED")
        self._badge.setStyleSheet(
            _BADGE_BASE + "QLabel { background-color: #252930; color: #6b7280; }"
        )
        self._name_lbl.setText("")
        self._detail_lbl.setText("")
        self._disconnect_btn.setEnabled(False)

    def set_connecting(self, ip: str) -> None:
        self._led.set_yellow()
        self._badge.setText("CONNECTING")
        self._badge.setStyleSheet(
            _BADGE_BASE + "QLabel { background-color: #2d2818; color: #ffb703; }"
        )
        self._name_lbl.setText("")
        self._detail_lbl.setText(f"   {ip}  …")
        self._disconnect_btn.setEnabled(False)

    def set_error(self, msg: str) -> None:
        self._led.set_red()
        self._badge.setText("ERROR")
        self._badge.setStyleSheet(
            _BADGE_BASE + "QLabel { background-color: #3a1a1c; color: #e63946; }"
        )
        self._name_lbl.setText("")
        self._detail_lbl.setText(f"   {msg}")
        self._disconnect_btn.setEnabled(False)
