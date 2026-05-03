from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import ConnectionConfig, PLCType
from plc_tools.communication.project_manager import ProjectEntry, ProjectManager


class ConnectDialog(QDialog):
    def __init__(self, project_manager: ProjectManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Connect to PLC")
        self.setMinimumWidth(380)
        self._pm = project_manager
        self._result_config: ConnectionConfig | None = None

        self._recent_combo = QComboBox()
        self._recent_combo.addItem("— New connection —")
        for entry in project_manager.entries:
            self._recent_combo.addItem(f"{entry.name}  ({entry.ip_address})", userData=entry)
        self._recent_combo.currentIndexChanged.connect(self._on_recent_changed)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("My PLC")

        self._ip_edit = QLineEdit()
        self._ip_edit.setPlaceholderText("192.168.1.1")

        self._slot_spin = QSpinBox()
        self._slot_spin.setRange(0, 17)

        self._type_combo = QComboBox()
        self._type_combo.addItem("ControlLogix / CompactLogix", userData=PLCType.LOGIX)
        self._type_combo.addItem("Micro800", userData=PLCType.MICRO800)
        self._type_combo.addItem("Mock (offline testing)", userData=PLCType.MOCK)

        form = QFormLayout()
        form.addRow("Name:", self._name_edit)
        form.addRow("IP Address:", self._ip_edit)
        form.addRow("Slot:", self._slot_spin)
        form.addRow("PLC Type:", self._type_combo)

        group = QGroupBox("Connection Details")
        group.setLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Recent connections:"))
        layout.addWidget(self._recent_combo)
        layout.addWidget(group)
        layout.addWidget(buttons)

    def _on_recent_changed(self, index: int) -> None:
        entry: ProjectEntry | None = self._recent_combo.currentData()
        if entry is None:
            return
        self._name_edit.setText(entry.name)
        self._ip_edit.setText(entry.ip_address)
        self._slot_spin.setValue(entry.slot)
        for i in range(self._type_combo.count()):
            if self._type_combo.itemData(i) == PLCType(entry.plc_type):
                self._type_combo.setCurrentIndex(i)
                break

    def _on_accept(self) -> None:
        ip = self._ip_edit.text().strip()
        if not ip:
            self._ip_edit.setFocus()
            return
        name = self._name_edit.text().strip() or ip
        plc_type: PLCType = self._type_combo.currentData()
        self._result_config = ConnectionConfig(
            ip_address=ip,
            slot=self._slot_spin.value(),
            plc_type=plc_type,
            name=name,
        )
        self._pm.add(ProjectEntry(
            name=name,
            ip_address=ip,
            slot=self._slot_spin.value(),
            plc_type=plc_type.value,
        ))
        self.accept()

    @property
    def config(self) -> ConnectionConfig | None:
        return self._result_config
