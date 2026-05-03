from __future__ import annotations

from PySide6.QtCore import Qt
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


class TagListTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tags: list[TagValue] = []

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter tags…")
        self._search.textChanged.connect(self._apply_filter)

        self._refresh_btn = QPushButton("Refresh")

        top = QHBoxLayout()
        top.addWidget(QLabel("Search:"))
        top.addWidget(self._search)
        top.addWidget(self._refresh_btn)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Tag Name", "Data Type", "Dimensions"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setSortingEnabled(True)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._table)

    def load_tags(self, tags: list[TagValue]) -> None:
        self._tags = tags
        self._apply_filter(self._search.text())

    def _apply_filter(self, text: str) -> None:
        lower = text.lower()
        filtered = [t for t in self._tags if lower in t.name.lower()]
        self._table.setRowCount(len(filtered))
        for row, tag in enumerate(filtered):
            self._table.setItem(row, 0, QTableWidgetItem(tag.name))
            self._table.setItem(row, 1, QTableWidgetItem(tag.data_type))
            self._table.setItem(row, 2, QTableWidgetItem(""))

    def clear(self) -> None:
        self._tags = []
        self._table.setRowCount(0)
