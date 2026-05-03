from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import TagValue
from plc_tools.gui.widgets.tag_browser import TagBrowser


class TagMonitorTab(QWidget):
    poll_interval_changed = Signal(int)
    tag_added = Signal(str)
    tag_removed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._watched: list[str] = []

        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(100, 10000)
        self._interval_spin.setValue(1000)
        self._interval_spin.setSuffix(" ms")
        self._interval_spin.valueChanged.connect(self.poll_interval_changed)

        self._add_btn = QPushButton("Add Tag…")
        self._remove_btn = QPushButton("Remove")
        self._clear_btn = QPushButton("Clear All")
        self._add_btn.clicked.connect(self._on_add)
        self._remove_btn.clicked.connect(self._on_remove)
        self._clear_btn.clicked.connect(self._on_clear)

        top = QHBoxLayout()
        top.addWidget(QLabel("Poll interval:"))
        top.addWidget(self._interval_spin)
        top.addStretch()
        top.addWidget(self._add_btn)
        top.addWidget(self._remove_btn)
        top.addWidget(self._clear_btn)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Tag Name", "Value", "Type", "Timestamp"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._table)

        self._browser: TagBrowser | None = None
        self._available_tags: list[TagValue] = []

    def set_available_tags(self, tags: list[TagValue]) -> None:
        self._available_tags = tags

    def update_values(self, values: list[TagValue]) -> None:
        val_map = {v.name: v for v in values}
        for row in range(self._table.rowCount()):
            name = self._table.item(row, 0).text()
            if name in val_map:
                tag = val_map[name]
                val_str = str(tag.value) if tag.is_valid else f"ERR: {tag.error}"
                ts_str = tag.timestamp.strftime("%H:%M:%S.%f")[:-3]
                self._table.item(row, 1).setText(val_str)
                self._table.item(row, 2).setText(tag.data_type)
                self._table.item(row, 3).setText(ts_str)
                color = QColor("#ff4444") if not tag.is_valid else QColor("#ffffff")
                for col in range(4):
                    self._table.item(row, col).setForeground(color)

    def _on_add(self) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

        dlg = QDialog(self)
        dlg.setWindowTitle("Add Tag to Monitor")
        dlg.setMinimumSize(400, 300)
        browser = TagBrowser(dlg)
        browser.load_tags(self._available_tags)
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(dlg.reject)
        layout = QVBoxLayout(dlg)
        layout.addWidget(browser)
        layout.addWidget(buttons)

        def _select(name: str) -> None:
            self._add_tag(name)
            dlg.accept()

        browser.tag_selected.connect(_select)
        dlg.exec()

    def _add_tag(self, name: str) -> None:
        if name in self._watched:
            return
        self._watched.append(name)
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(name))
        self._table.setItem(row, 1, QTableWidgetItem("—"))
        self._table.setItem(row, 2, QTableWidgetItem("—"))
        self._table.setItem(row, 3, QTableWidgetItem("—"))
        self.tag_added.emit(name)

    def _on_remove(self) -> None:
        rows = {idx.row() for idx in self._table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            name = self._table.item(row, 0).text()
            self._watched.remove(name)
            self._table.removeRow(row)
            self.tag_removed.emit(name)

    def _on_clear(self) -> None:
        for name in list(self._watched):
            self.tag_removed.emit(name)
        self._watched.clear()
        self._table.setRowCount(0)

    @property
    def watched_tags(self) -> list[str]:
        return list(self._watched)

    def clear(self) -> None:
        self._on_clear()
