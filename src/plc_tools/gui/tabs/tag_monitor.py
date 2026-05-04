from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
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

_MONO = QFont("Consolas", 12)
_MONO_SMALL = QFont("Consolas", 10)


class TagMonitorTab(QWidget):
    poll_interval_changed = Signal(int)
    tag_added   = Signal(str)
    tag_removed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._watched: list[str] = []
        self._available_tags: list[TagValue] = []

        # ── Controls row ──────────────────────────────────────────────────────
        interval_lbl = QLabel("Poll:")
        interval_lbl.setStyleSheet("QLabel { color: #8b95a5; font-size: 12px; }")

        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(100, 10000)
        self._interval_spin.setValue(1000)
        self._interval_spin.setSuffix(" ms")
        self._interval_spin.setFixedWidth(100)
        self._interval_spin.valueChanged.connect(self.poll_interval_changed)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(18)
        sep.setStyleSheet("QFrame { color: #383e50; }")

        self._add_btn    = QPushButton("+ Add Tag")
        self._remove_btn = QPushButton("Remove")
        self._remove_btn.setObjectName("refresh_btn")
        self._clear_btn  = QPushButton("Clear All")
        self._clear_btn.setObjectName("refresh_btn")
        self._tag_count_lbl = QLabel("")
        self._tag_count_lbl.setStyleSheet("QLabel { color: #8b95a5; font-size: 11px; }")

        self._add_btn.clicked.connect(self._on_add)
        self._remove_btn.clicked.connect(self._on_remove)
        self._clear_btn.clicked.connect(self._on_clear)

        top = QHBoxLayout()
        top.setContentsMargins(0, 8, 0, 4)
        top.setSpacing(8)
        top.addWidget(interval_lbl)
        top.addWidget(self._interval_spin)
        top.addWidget(sep)
        top.addStretch()
        top.addWidget(self._tag_count_lbl)
        top.addWidget(self._add_btn)
        top.addWidget(self._remove_btn)
        top.addWidget(self._clear_btn)

        # ── Monitor table ─────────────────────────────────────────────────────
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Tag Name", "Value", "Type", "Last Update"])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(34)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 16)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(self._table)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_available_tags(self, tags: list[TagValue]) -> None:
        self._available_tags = tags

    def update_values(self, values: list[TagValue]) -> None:
        val_map = {v.name: v for v in values}
        for row in range(self._table.rowCount()):
            name = self._table.item(row, 0).text()
            if name not in val_map:
                continue
            tag = val_map[name]

            if tag.is_valid:
                val_str = str(tag.value)
                # Colour-code by data type
                if tag.data_type == "BOOL":
                    val_color = QColor("#3dd68c") if tag.value else QColor("#6b7280")
                elif tag.data_type in ("REAL", "LREAL"):
                    val_color = QColor("#fbbf24")
                else:
                    val_color = QColor("#e8eaf0")
            else:
                val_str = f"ERR: {tag.error}"
                val_color = QColor("#e63946")

            ts_str = tag.timestamp.strftime("%H:%M:%S.%f")[:-3]

            val_item = self._table.item(row, 1)
            type_item = self._table.item(row, 2)
            ts_item = self._table.item(row, 3)

            val_item.setText(val_str)
            val_item.setForeground(val_color)
            type_item.setText(tag.data_type)
            type_item.setForeground(QColor("#8b95a5"))
            ts_item.setText(ts_str)
            ts_item.setForeground(QColor("#555f6d"))

    # ── Private helpers ───────────────────────────────────────────────────────

    def _on_add(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Tag to Monitor")
        dlg.setMinimumSize(440, 360)
        browser = TagBrowser(dlg)
        browser.load_tags(self._available_tags)
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(dlg.reject)
        vlay = QVBoxLayout(dlg)
        vlay.addWidget(browser)
        vlay.addWidget(buttons)

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

        name_item = QTableWidgetItem(name)
        name_item.setFont(_MONO)

        val_item  = QTableWidgetItem("—")
        val_item.setFont(_MONO)
        val_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        type_item = QTableWidgetItem("—")
        type_item.setFont(_MONO_SMALL)
        type_item.setTextAlignment(Qt.AlignCenter)
        type_item.setForeground(QColor("#8b95a5"))

        ts_item = QTableWidgetItem("—")
        ts_item.setFont(_MONO_SMALL)
        ts_item.setTextAlignment(Qt.AlignCenter)
        ts_item.setForeground(QColor("#555f6d"))

        self._table.setItem(row, 0, name_item)
        self._table.setItem(row, 1, val_item)
        self._table.setItem(row, 2, type_item)
        self._table.setItem(row, 3, ts_item)
        self.tag_added.emit(name)
        self._update_count()

    def _on_remove(self) -> None:
        rows = {idx.row() for idx in self._table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            name = self._table.item(row, 0).text()
            self._watched.remove(name)
            self._table.removeRow(row)
            self.tag_removed.emit(name)
        self._update_count()

    def _on_clear(self) -> None:
        for name in list(self._watched):
            self.tag_removed.emit(name)
        self._watched.clear()
        self._table.setRowCount(0)
        self._update_count()

    def _update_count(self) -> None:
        n = len(self._watched)
        self._tag_count_lbl.setText(f"{n} tag{'s' if n != 1 else ''}" if n else "")

    @property
    def watched_tags(self) -> list[str]:
        return list(self._watched)

    def clear(self) -> None:
        self._on_clear()
