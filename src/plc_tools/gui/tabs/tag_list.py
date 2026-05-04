from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import TagValue

# Color-code common data types for quick recognition
_TYPE_COLORS = {
    "BOOL":  "#60a5fa",
    "DINT":  "#a78bfa",
    "INT":   "#a78bfa",
    "UINT":  "#a78bfa",
    "REAL":  "#34d399",
    "LREAL": "#34d399",
    "DWORD": "#fbbf24",
    "WORD":  "#fbbf24",
    "USINT": "#a78bfa",
}


class TagListTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tags: list[TagValue] = []

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter by tag name…")
        self._search.textChanged.connect(self._apply_filter)

        self._refresh_btn = QPushButton("↻  Refresh")
        self._refresh_btn.setObjectName("refresh_btn")

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet("QLabel { color: #8b95a5; font-size: 11px; }")

        top = QHBoxLayout()
        top.setContentsMargins(0, 8, 0, 4)
        top.setSpacing(8)
        top.addWidget(self._search)
        top.addWidget(self._refresh_btn)
        top.addWidget(self._count_lbl)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Tag Name", "Data Type"])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(30)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 16)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(self._table)

    def load_tags(self, tags: list[TagValue]) -> None:
        self._tags = tags
        self._apply_filter(self._search.text())

    def _apply_filter(self, text: str) -> None:
        lower = text.lower()
        filtered = [t for t in self._tags if lower in t.name.lower()]
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(filtered))
        mono = QFont("Consolas", 11)
        for row, tag in enumerate(filtered):
            name_item = QTableWidgetItem(tag.name)
            name_item.setFont(mono)

            type_item = QTableWidgetItem(tag.data_type)
            type_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            type_item.setTextAlignment(Qt.AlignCenter)
            type_item.setForeground(
                QColor(_TYPE_COLORS.get(tag.data_type, "#8b95a5"))
            )

            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, type_item)

        self._table.setSortingEnabled(True)
        total = len(self._tags)
        shown = len(filtered)
        if total:
            self._count_lbl.setText(
                f"{shown} of {total}" if text else f"{total} tags"
            )

    def clear(self) -> None:
        self._tags = []
        self._table.setRowCount(0)
        self._count_lbl.setText("")
