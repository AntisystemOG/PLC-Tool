from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
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


def _build_type_combo() -> QComboBox:
    combo = QComboBox()
    model = QStandardItemModel(combo)

    def _add_header(label: str) -> None:
        item = QStandardItem(label)
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        item.setFlags(item.flags() & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)
        model.appendRow(item)

    def _add_item(label: str, plc_type: PLCType) -> None:
        item = QStandardItem(label)
        item.setData(plc_type, Qt.UserRole)
        model.appendRow(item)

    _add_item("ControlLogix / CompactLogix", PLCType.LOGIX)
    _add_header("── Micro800 Series (CCW) ──")
    _add_item("  Micro810  (2080-LC10)", PLCType.MICRO810)
    _add_item("  Micro820  (2080-LC20)", PLCType.MICRO820)
    _add_item("  Micro830  (2080-LC30)", PLCType.MICRO830)
    _add_item("  Micro850  (2080-LC50)", PLCType.MICRO850)
    _add_item("  Micro870  (2080-LC70)", PLCType.MICRO870)
    _add_header("──────────────────────────")
    _add_item("Mock / Demo (offline)", PLCType.MOCK)

    combo.setModel(model)
    combo.setCurrentIndex(0)
    return combo


class ConnectDialog(QDialog):
    def __init__(self, project_manager: ProjectManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Connect to PLC")
        self.setMinimumWidth(400)
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

        self._type_combo = _build_type_combo()

        form = QFormLayout()
        form.addRow("Name:", self._name_edit)
        form.addRow("IP Address:", self._ip_edit)
        form.addRow("Slot:", self._slot_spin)
        form.addRow("PLC Type:", self._type_combo)

        group = QGroupBox("Connection Details")
        group.setLayout(form)

        self._demo_btn = QPushButton("Load Demo  (Micro850 — no PLC required)")
        self._demo_btn.setToolTip(
            "Pre-fills all fields for the offline Micro850 demo.\n"
            "No physical PLC or network connection is needed."
        )
        self._demo_btn.clicked.connect(self._load_demo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Recent connections:"))
        layout.addWidget(self._recent_combo)
        layout.addWidget(group)
        layout.addWidget(self._demo_btn)
        layout.addWidget(buttons)

    def _select_type(self, plc_type: PLCType) -> None:
        model: QStandardItemModel = self._type_combo.model()
        for i in range(model.rowCount()):
            item = model.item(i)
            if item and item.data(Qt.UserRole) == plc_type:
                self._type_combo.setCurrentIndex(i)
                return

    def _on_recent_changed(self, index: int) -> None:
        entry: ProjectEntry | None = self._recent_combo.currentData()
        if entry is None:
            return
        self._name_edit.setText(entry.name)
        self._ip_edit.setText(entry.ip_address)
        self._slot_spin.setValue(entry.slot)
        try:
            self._select_type(PLCType(entry.plc_type))
        except ValueError:
            pass

    def _load_demo(self) -> None:
        self._name_edit.setText("Demo Micro850")
        self._ip_edit.setText("127.0.0.1")
        self._slot_spin.setValue(0)
        self._select_type(PLCType.MOCK)
        self._on_accept()

    def _on_accept(self) -> None:
        ip = self._ip_edit.text().strip()
        if not ip:
            self._ip_edit.setFocus()
            return
        plc_type: PLCType | None = self._type_combo.currentData(Qt.UserRole)
        if plc_type is None:
            return   # header row somehow selected — do nothing
        name = self._name_edit.text().strip() or ip
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
