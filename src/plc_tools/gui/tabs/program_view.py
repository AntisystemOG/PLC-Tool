from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
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


class ProgramViewTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._refresh_btn = QPushButton("Refresh")
        top = QHBoxLayout()
        top.addWidget(self._refresh_btn)
        top.addStretch()

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Program / Routine", "Type"])
        self._tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tree.currentItemChanged.connect(self._on_item_changed)

        self._detail_table = QTableWidget(0, 2)
        self._detail_table.setHorizontalHeaderLabels(["Property", "Value"])
        self._detail_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._detail_table.setEditTriggers(QTableWidget.NoEditTriggers)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._tree)
        splitter.addWidget(self._detail_table)
        splitter.setSizes([250, 350])

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(splitter)

    def load_programs(self, programs: list[ProgramInfo]) -> None:
        self._tree.clear()
        for prog in programs:
            prog_item = QTreeWidgetItem([prog.name, prog.program_type])
            prog_item.setData(0, Qt.UserRole, ("program", prog))
            for routine in prog.routines:
                r_item = QTreeWidgetItem([routine.name, routine.routine_type])
                r_item.setData(0, Qt.UserRole, ("routine", routine))
                prog_item.addChild(r_item)
            self._tree.addTopLevelItem(prog_item)
        self._tree.expandAll()

    def _on_item_changed(self, current: QTreeWidgetItem | None, _: object) -> None:
        self._detail_table.setRowCount(0)
        if current is None:
            return
        kind, obj = current.data(0, Qt.UserRole) or (None, None)
        if kind == "program":
            rows = [
                ("Name", obj.name),
                ("Type", obj.program_type),
                ("Routines", str(len(obj.routines))),
            ]
        elif kind == "routine":
            rows = [
                ("Name", obj.name),
                ("Type", obj.routine_type),
            ]
        else:
            return
        self._detail_table.setRowCount(len(rows))
        for r, (prop, val) in enumerate(rows):
            self._detail_table.setItem(r, 0, QTableWidgetItem(prop))
            self._detail_table.setItem(r, 1, QTableWidgetItem(val))

    def clear(self) -> None:
        self._tree.clear()
        self._detail_table.setRowCount(0)
