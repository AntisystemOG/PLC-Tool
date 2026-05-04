from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import ProgramInfo

_ROUTINE_TYPE_COLORS = {
    "LAD":  "#60a5fa",
    "ST":   "#a78bfa",
    "FBD":  "#34d399",
    "SFC":  "#fbbf24",
}


class ProgramViewTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._refresh_btn = QPushButton("↻  Refresh")
        self._refresh_btn.setObjectName("refresh_btn")
        top = QHBoxLayout()
        top.setContentsMargins(0, 8, 0, 4)
        top.addWidget(self._refresh_btn)
        top.addStretch()

        # ── Program tree (left) ───────────────────────────────────────────────
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Program / Routine", "Language"])
        self._tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._tree.setAlternatingRowColors(True)
        self._tree.currentItemChanged.connect(self._on_item_changed)

        # ── Detail panel (right) ──────────────────────────────────────────────
        self._detail_header = QLabel("Select a program or routine")
        self._detail_header.setStyleSheet(
            "QLabel { color: #8b95a5; font-size: 11px; padding: 4px 0; }"
        )
        self._detail_table = QTableWidget(0, 2)
        self._detail_table.setHorizontalHeaderLabels(["Property", "Value"])
        self._detail_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._detail_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._detail_table.verticalHeader().setVisible(False)
        self._detail_table.setAlternatingRowColors(True)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.addWidget(self._detail_header)
        right_layout.addWidget(self._detail_table)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._tree)
        splitter.addWidget(right_panel)
        splitter.setSizes([280, 320])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 16)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(splitter)

    def load_programs(self, programs: list[ProgramInfo]) -> None:
        self._tree.clear()
        bold = QFont("Segoe UI", 12, QFont.Bold)

        for prog in programs:
            prog_item = QTreeWidgetItem([prog.name, prog.program_type])
            prog_item.setData(0, Qt.UserRole, ("program", prog))
            prog_item.setFont(0, bold)
            prog_item.setForeground(0, QColor("#e8eaf0"))
            prog_item.setForeground(1, QColor("#8b95a5"))

            for routine in prog.routines:
                r_item = QTreeWidgetItem([f"  {routine.name}", routine.routine_type])
                r_item.setData(0, Qt.UserRole, ("routine", routine))
                lang_color = _ROUTINE_TYPE_COLORS.get(routine.routine_type, "#8b95a5")
                r_item.setForeground(1, QColor(lang_color))
                prog_item.addChild(r_item)

            self._tree.addTopLevelItem(prog_item)

        self._tree.expandAll()

    def _on_item_changed(self, current: QTreeWidgetItem | None, _: object) -> None:
        self._detail_table.setRowCount(0)
        if current is None:
            return
        kind, obj = current.data(0, Qt.UserRole) or (None, None)

        if kind == "program":
            self._detail_header.setText(f"Program: {obj.name}")
            rows = [
                ("Name",      obj.name),
                ("Type",      obj.program_type),
                ("Routines",  str(len(obj.routines))),
            ]
        elif kind == "routine":
            self._detail_header.setText(f"Routine: {obj.name.strip()}")
            rows = [
                ("Name",     obj.name.strip()),
                ("Language", obj.routine_type),
            ]
        else:
            return

        self._detail_table.setRowCount(len(rows))
        for r, (prop, val) in enumerate(rows):
            key_item = QTableWidgetItem(prop)
            key_item.setForeground(QColor("#8b95a5"))
            val_item = QTableWidgetItem(val)
            val_item.setForeground(QColor("#e8eaf0"))
            if prop == "Language":
                val_item.setForeground(QColor(_ROUTINE_TYPE_COLORS.get(val, "#8b95a5")))
            self._detail_table.setItem(r, 0, key_item)
            self._detail_table.setItem(r, 1, val_item)

    def clear(self) -> None:
        self._tree.clear()
        self._detail_table.setRowCount(0)
        self._detail_header.setText("Select a program or routine")
