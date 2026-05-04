from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import FaultEntry, FaultType

# (row background tint,  type-badge text color,  badge background)
_FAULT_STYLES = {
    FaultType.MAJOR: ("#2a1214", "#f87171", "#4a1a1c"),
    FaultType.MINOR: ("#252010", "#fbbf24", "#3f3010"),
    FaultType.IO:    ("#121c2e", "#60a5fa", "#1a2d4a"),
}


class FaultLogTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._refresh_btn = QPushButton("↻  Refresh")
        self._refresh_btn.setObjectName("refresh_btn")
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("refresh_btn")
        self._clear_btn.clicked.connect(self._table_clear)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet("QLabel { color: #8b95a5; font-size: 11px; }")

        top = QHBoxLayout()
        top.setContentsMargins(0, 8, 0, 4)
        top.addWidget(self._refresh_btn)
        top.addWidget(self._clear_btn)
        top.addStretch()
        top.addWidget(self._count_lbl)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(
            ["Timestamp", "Type", "Code", "Program", "Description"]
        )
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setDefaultSectionSize(34)
        self._table.verticalHeader().setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 16)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(self._table)

    def load_faults(self, faults: list[FaultEntry]) -> None:
        self._table.setRowCount(len(faults))
        mono = QFont("Consolas", 11)

        for row, fault in enumerate(faults):
            row_bg, badge_fg, badge_bg = _FAULT_STYLES.get(
                fault.fault_type, ("#1e2128", "#c0c4d0", "#2d3240")
            )
            ts = fault.timestamp.strftime("%Y-%m-%d  %H:%M:%S")

            items = [
                QTableWidgetItem(ts),
                QTableWidgetItem(f"  {fault.fault_type.value.upper()}  "),
                QTableWidgetItem(f"0x{fault.code:04X}"),
                QTableWidgetItem(fault.program),
                QTableWidgetItem(fault.description),
            ]

            row_color = QColor(row_bg)
            for col, item in enumerate(items):
                item.setBackground(row_color)
                self._table.setItem(row, col, item)

            # Type badge — distinct color per severity
            badge_item = self._table.item(row, 1)
            badge_item.setForeground(QColor(badge_fg))
            badge_item.setBackground(QColor(badge_bg))
            badge_item.setTextAlignment(Qt.AlignCenter)
            badge_item.setFont(QFont("Segoe UI", 10, QFont.Bold))

            # Timestamp + code in monospace
            for col in (0, 2):
                self._table.item(row, col).setFont(mono)
                self._table.item(row, col).setForeground(QColor("#8b95a5"))

        count = len(faults)
        self._count_lbl.setText(
            f"{count} fault{'s' if count != 1 else ''}" if count else ""
        )

    def _table_clear(self) -> None:
        self._table.setRowCount(0)
        self._count_lbl.setText("")

    def clear(self) -> None:
        self._table_clear()
