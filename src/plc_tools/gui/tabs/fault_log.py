from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import FaultEntry, FaultType

_FAULT_COLORS = {
    FaultType.MAJOR: QColor("#ff6666"),
    FaultType.MINOR: QColor("#ffcc66"),
    FaultType.IO: QColor("#66aaff"),
}


class FaultLogTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._refresh_btn = QPushButton("Refresh")
        self._clear_btn = QPushButton("Clear Display")
        self._clear_btn.clicked.connect(self._table_clear)

        top = QHBoxLayout()
        top.addWidget(self._refresh_btn)
        top.addWidget(self._clear_btn)
        top.addStretch()

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Timestamp", "Type", "Code", "Program", "Description"])
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._table)

    def load_faults(self, faults: list[FaultEntry]) -> None:
        self._table.setRowCount(len(faults))
        for row, fault in enumerate(faults):
            color = _FAULT_COLORS.get(fault.fault_type, QColor("#ffffff"))
            ts = fault.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            items = [
                QTableWidgetItem(ts),
                QTableWidgetItem(fault.fault_type.value.upper()),
                QTableWidgetItem(f"0x{fault.code:04X}"),
                QTableWidgetItem(fault.program),
                QTableWidgetItem(fault.description),
            ]
            for col, item in enumerate(items):
                item.setBackground(color)
                self._table.setItem(row, col, item)

    def _table_clear(self) -> None:
        self._table.setRowCount(0)

    def clear(self) -> None:
        self._table_clear()
