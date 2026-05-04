from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import ControllerInfo
from plc_tools.gui.widgets.status_led import StatusLed

_LABEL_STYLE = "QLabel { color: #8b95a5; font-size: 11px; }"
_VALUE_STYLE = "QLabel { color: #e8eaf0; font-family: Consolas, monospace; font-size: 13px; }"


def _make_row(label: str) -> tuple[QLabel, QLabel]:
    lbl = QLabel(label)
    lbl.setStyleSheet(_LABEL_STYLE)
    val = QLabel("—")
    val.setStyleSheet(_VALUE_STYLE)
    return lbl, val


class DiagnosticsTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # ── Toolbar ──────────────────────────────────────────────────────────
        self._refresh_btn = QPushButton("↻  Refresh")
        self._refresh_btn.setObjectName("refresh_btn")
        top = QHBoxLayout()
        top.setContentsMargins(0, 8, 0, 4)
        top.addWidget(self._refresh_btn)
        top.addStretch()

        # ── Controller Information card ───────────────────────────────────────
        info_group = QGroupBox("CONTROLLER INFORMATION")
        info_form = QFormLayout(info_group)
        info_form.setHorizontalSpacing(20)
        info_form.setVerticalSpacing(10)

        _, self._lbl_name      = _make_row("Name")
        _, self._lbl_catalog   = _make_row("Catalog")
        _, self._lbl_firmware  = _make_row("Firmware")
        _, self._lbl_serial    = _make_row("Serial")
        _, self._lbl_keyswitch = _make_row("Keyswitch")

        for key, val in [
            ("Name",       self._lbl_name),
            ("Catalog:",   self._lbl_catalog),
            ("Firmware:",  self._lbl_firmware),
            ("Serial:",    self._lbl_serial),
            ("Keyswitch:", self._lbl_keyswitch),
        ]:
            row_lbl = QLabel(key)
            row_lbl.setStyleSheet(_LABEL_STYLE)
            info_form.addRow(row_lbl, val)

        # ── Runtime Status card ───────────────────────────────────────────────
        status_group = QGroupBox("RUNTIME STATUS")
        status_layout = QFormLayout(status_group)
        status_layout.setHorizontalSpacing(20)
        status_layout.setVerticalSpacing(12)

        self._status_led = StatusLed("gray")
        self._lbl_status = QLabel("—")
        self._lbl_status.setStyleSheet(_VALUE_STYLE)
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_row.addWidget(self._status_led)
        status_row.addWidget(self._lbl_status)
        status_row.addStretch()

        self._cpu_bar = QProgressBar()
        self._cpu_bar.setRange(0, 100)
        self._cpu_bar.setFormat("%v%")
        self._cpu_bar.setFixedHeight(20)

        self._mem_bar = QProgressBar()
        self._mem_bar.setRange(0, 100)
        self._mem_bar.setFormat("%v%")
        self._mem_bar.setFixedHeight(20)

        for key, widget in [
            ("Status:",  status_row),
            ("CPU Load:", self._cpu_bar),
            ("Memory:",   self._mem_bar),
        ]:
            row_lbl = QLabel(key)
            row_lbl.setStyleSheet(_LABEL_STYLE)
            status_layout.addRow(row_lbl, widget)

        # ── Main layout ───────────────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 16)
        layout.setSpacing(12)
        layout.addLayout(top)
        layout.addWidget(info_group)
        layout.addWidget(status_group)
        layout.addStretch()

    # ── Public API ────────────────────────────────────────────────────────────

    def load_info(self, info: ControllerInfo) -> None:
        self._lbl_name.setText(info.name)
        self._lbl_catalog.setText(info.catalog or "—")
        self._lbl_firmware.setText(info.firmware or "—")
        self._lbl_serial.setText(info.serial_number or "—")
        self._lbl_keyswitch.setText(info.keyswitch)
        self._lbl_status.setText(info.status)

        running = "run" in info.status.lower()
        if running:
            self._status_led.set_green()
            self._lbl_status.setStyleSheet(
                "QLabel { color: #3dd68c; font-family: Consolas, monospace; font-size: 13px; font-weight: bold; }"
            )
        else:
            self._status_led.set_red()
            self._lbl_status.setStyleSheet(
                "QLabel { color: #e63946; font-family: Consolas, monospace; font-size: 13px; font-weight: bold; }"
            )

        cpu = int(info.cpu_load)
        self._cpu_bar.setValue(cpu)
        self._cpu_bar.setFormat(f"{cpu}%")
        if cpu > 80:
            self._cpu_bar.setStyleSheet("QProgressBar::chunk { background: #e63946; }")
        elif cpu > 60:
            self._cpu_bar.setStyleSheet("QProgressBar::chunk { background: #ffb703; }")
        else:
            self._cpu_bar.setStyleSheet("")

        mem = int(info.memory_percent)
        self._mem_bar.setValue(mem)
        mem_kb_used = info.memory_used // 1024
        mem_kb_total = info.memory_total // 1024
        self._mem_bar.setFormat(f"{mem}%  ({mem_kb_used} / {mem_kb_total} KB)")
        if mem > 80:
            self._mem_bar.setStyleSheet("QProgressBar::chunk { background: #e63946; }")
        else:
            self._mem_bar.setStyleSheet("")

    def clear(self) -> None:
        for lbl in (self._lbl_name, self._lbl_catalog, self._lbl_firmware,
                    self._lbl_serial, self._lbl_keyswitch, self._lbl_status):
            lbl.setText("—")
            lbl.setStyleSheet(_VALUE_STYLE)
        self._status_led.set_gray()
        self._cpu_bar.setValue(0)
        self._cpu_bar.setFormat("0%")
        self._mem_bar.setValue(0)
        self._mem_bar.setFormat("0%")
