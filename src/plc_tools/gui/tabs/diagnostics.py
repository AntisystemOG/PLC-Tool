from __future__ import annotations

from PySide6.QtCore import Qt
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


class DiagnosticsTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._refresh_btn = QPushButton("Refresh")
        top = QHBoxLayout()
        top.addWidget(self._refresh_btn)
        top.addStretch()

        info_group = QGroupBox("Controller Information")
        info_form = QFormLayout(info_group)
        self._lbl_name = QLabel("—")
        self._lbl_catalog = QLabel("—")
        self._lbl_firmware = QLabel("—")
        self._lbl_serial = QLabel("—")
        self._lbl_keyswitch = QLabel("—")
        info_form.addRow("Name:", self._lbl_name)
        info_form.addRow("Catalog:", self._lbl_catalog)
        info_form.addRow("Firmware:", self._lbl_firmware)
        info_form.addRow("Serial:", self._lbl_serial)
        info_form.addRow("Keyswitch:", self._lbl_keyswitch)

        status_group = QGroupBox("Runtime Status")
        status_layout = QFormLayout(status_group)
        self._status_led = StatusLed("gray")
        self._lbl_status = QLabel("—")
        status_row = QHBoxLayout()
        status_row.addWidget(self._status_led)
        status_row.addWidget(self._lbl_status)
        status_row.addStretch()

        self._cpu_bar = QProgressBar()
        self._cpu_bar.setRange(0, 100)
        self._cpu_bar.setFormat("%v%")

        self._mem_bar = QProgressBar()
        self._mem_bar.setRange(0, 100)
        self._mem_bar.setFormat("%v%")

        status_layout.addRow("Status:", status_row)
        status_layout.addRow("CPU Load:", self._cpu_bar)
        status_layout.addRow("Memory:", self._mem_bar)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(info_group)
        layout.addWidget(status_group)
        layout.addStretch()

    def load_info(self, info: ControllerInfo) -> None:
        self._lbl_name.setText(info.name)
        self._lbl_catalog.setText(info.catalog)
        self._lbl_firmware.setText(info.firmware)
        self._lbl_serial.setText(info.serial_number)
        self._lbl_keyswitch.setText(info.keyswitch)
        self._lbl_status.setText(info.status)

        running = "run" in info.status.lower()
        self._status_led.set_green() if running else self._status_led.set_red()

        self._cpu_bar.setValue(int(info.cpu_load))
        self._mem_bar.setValue(int(info.memory_percent))

    def clear(self) -> None:
        for lbl in (self._lbl_name, self._lbl_catalog, self._lbl_firmware,
                    self._lbl_serial, self._lbl_keyswitch, self._lbl_status):
            lbl.setText("—")
        self._status_led.set_gray()
        self._cpu_bar.setValue(0)
        self._mem_bar.setValue(0)
