from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import IOModule
from plc_tools.gui.widgets.status_led import StatusLed


class IOStatusTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._refresh_btn = QPushButton("Refresh")
        top = QHBoxLayout()
        top.addWidget(self._refresh_btn)
        top.addStretch()

        self._module_table = QTableWidget(0, 4)
        self._module_table.setHorizontalHeaderLabels(["Slot", "Catalog", "Name", "Status"])
        self._module_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._module_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._module_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._module_table.currentRowChanged.connect(self._on_module_selected)

        self._channel_table = QTableWidget(0, 3)
        self._channel_table.setHorizontalHeaderLabels(["Channel", "Name", "Value"])
        self._channel_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._channel_table.setEditTriggers(QTableWidget.NoEditTriggers)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._module_table)
        splitter.addWidget(self._channel_table)
        splitter.setSizes([300, 300])

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(splitter)

        self._modules: list[IOModule] = []

    def load_modules(self, modules: list[IOModule]) -> None:
        self._modules = modules
        self._module_table.setRowCount(len(modules))
        for row, mod in enumerate(modules):
            self._module_table.setItem(row, 0, QTableWidgetItem(str(mod.slot)))
            self._module_table.setItem(row, 1, QTableWidgetItem(mod.catalog))
            self._module_table.setItem(row, 2, QTableWidgetItem(mod.name))
            status_item = QTableWidgetItem(mod.status)
            if mod.is_faulted:
                status_item.setForeground(QColor("#ff4444"))
            self._module_table.setItem(row, 3, status_item)

    def _on_module_selected(self, row: int) -> None:
        if row < 0 or row >= len(self._modules):
            self._channel_table.setRowCount(0)
            return
        mod = self._modules[row]
        self._channel_table.setRowCount(len(mod.channels))
        for r, ch in enumerate(mod.channels):
            direction = "IN" if ch.is_input else "OUT"
            self._channel_table.setItem(r, 0, QTableWidgetItem(f"{direction} {ch.channel}"))
            self._channel_table.setItem(r, 1, QTableWidgetItem(ch.name))
            val_item = QTableWidgetItem(str(ch.value))
            if isinstance(ch.value, bool) and ch.value:
                val_item.setForeground(QColor("#00cc44"))
            self._channel_table.setItem(r, 2, val_item)

    def clear(self) -> None:
        self._modules = []
        self._module_table.setRowCount(0)
        self._channel_table.setRowCount(0)
