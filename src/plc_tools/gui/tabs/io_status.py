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
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import IOModule


class IOStatusTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._refresh_btn = QPushButton("↻  Refresh")
        self._refresh_btn.setObjectName("refresh_btn")
        self._module_count_lbl = QLabel("")
        self._module_count_lbl.setStyleSheet("QLabel { color: #8b95a5; font-size: 11px; }")

        top = QHBoxLayout()
        top.setContentsMargins(0, 8, 0, 4)
        top.addWidget(self._refresh_btn)
        top.addStretch()
        top.addWidget(self._module_count_lbl)

        # ── Module list (left pane) ───────────────────────────────────────────
        self._module_table = QTableWidget(0, 4)
        self._module_table.setHorizontalHeaderLabels(["Slot", "Catalog", "Module Name", "Status"])
        hdr = self._module_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._module_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._module_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._module_table.setAlternatingRowColors(True)
        self._module_table.verticalHeader().setVisible(False)
        self._module_table.currentCellChanged.connect(self._on_module_selected)

        # ── Channel detail (right pane) ───────────────────────────────────────
        self._channel_header = QLabel("Select a module to view channels")
        self._channel_header.setStyleSheet(
            "QLabel { color: #8b95a5; font-size: 11px; padding: 4px 0; }"
        )

        self._channel_table = QTableWidget(0, 4)
        self._channel_table.setHorizontalHeaderLabels(["Dir", "Ch", "Name", "Value"])
        chdr = self._channel_table.horizontalHeader()
        chdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        chdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        chdr.setSectionResizeMode(2, QHeaderView.Stretch)
        chdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._channel_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._channel_table.setAlternatingRowColors(True)
        self._channel_table.verticalHeader().setVisible(False)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.addWidget(self._channel_header)
        right_layout.addWidget(self._channel_table)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._module_table)
        splitter.addWidget(right_panel)
        splitter.setSizes([340, 360])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 16)
        layout.setSpacing(8)
        layout.addLayout(top)
        layout.addWidget(splitter)

        self._modules: list[IOModule] = []

    def load_modules(self, modules: list[IOModule]) -> None:
        self._modules = modules
        self._module_table.setRowCount(len(modules))
        mono = QFont("Consolas", 11)

        for row, mod in enumerate(modules):
            slot_item = QTableWidgetItem(str(mod.slot))
            slot_item.setTextAlignment(Qt.AlignCenter)
            slot_item.setFont(mono)

            catalog_item = QTableWidgetItem(mod.catalog)
            catalog_item.setFont(mono)
            catalog_item.setForeground(QColor("#8b95a5"))

            self._module_table.setItem(row, 0, slot_item)
            self._module_table.setItem(row, 1, catalog_item)
            self._module_table.setItem(row, 2, QTableWidgetItem(mod.name))

            status_item = QTableWidgetItem(mod.status)
            status_item.setTextAlignment(Qt.AlignCenter)
            if mod.is_faulted:
                status_item.setForeground(QColor("#e63946"))
                status_item.setBackground(QColor("#3a1a1c"))
            else:
                status_item.setForeground(QColor("#3dd68c"))
            self._module_table.setItem(row, 3, status_item)

        count = len(modules)
        self._module_count_lbl.setText(
            f"{count} module{'s' if count != 1 else ''}" if count else ""
        )

    def _on_module_selected(self, current_row: int, _cc: int, _pr: int, _pc: int) -> None:
        if current_row < 0 or current_row >= len(self._modules):
            self._channel_table.setRowCount(0)
            self._channel_header.setText("Select a module to view channels")
            return

        mod = self._modules[current_row]
        self._channel_header.setText(
            f"{mod.name}  —  {len(mod.channels)} channel{'s' if len(mod.channels) != 1 else ''}"
        )
        self._channel_table.setRowCount(len(mod.channels))
        mono = QFont("Consolas", 11)

        for r, ch in enumerate(mod.channels):
            dir_lbl = "IN " if ch.is_input else "OUT"
            dir_item = QTableWidgetItem(dir_lbl)
            dir_item.setTextAlignment(Qt.AlignCenter)
            dir_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            dir_item.setForeground(
                QColor("#60a5fa") if ch.is_input else QColor("#fb923c")
            )

            ch_num = QTableWidgetItem(str(ch.channel))
            ch_num.setTextAlignment(Qt.AlignCenter)
            ch_num.setFont(mono)
            ch_num.setForeground(QColor("#8b95a5"))

            name_item = QTableWidgetItem(ch.name)
            name_item.setFont(mono)

            val_str = str(ch.value)
            val_item = QTableWidgetItem(val_str)
            val_item.setFont(mono)
            val_item.setTextAlignment(Qt.AlignCenter)
            if isinstance(ch.value, bool):
                val_item.setForeground(
                    QColor("#3dd68c") if ch.value else QColor("#6b7280")
                )
            elif isinstance(ch.value, (int, float)):
                val_item.setForeground(QColor("#c0c4d0"))

            self._channel_table.setItem(r, 0, dir_item)
            self._channel_table.setItem(r, 1, ch_num)
            self._channel_table.setItem(r, 2, name_item)
            self._channel_table.setItem(r, 3, val_item)

    def clear(self) -> None:
        self._modules = []
        self._module_table.setRowCount(0)
        self._channel_table.setRowCount(0)
        self._channel_header.setText("Select a module to view channels")
        self._module_count_lbl.setText("")
