from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.models import TagValue


class TagBrowser(QWidget):
    tag_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._all_tags: list[TagValue] = []

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter tags…")
        self._search.textChanged.connect(self._apply_filter)

        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._list.itemDoubleClicked.connect(self._on_double_click)

        self._select_btn = QPushButton("Select")
        self._select_btn.clicked.connect(self._on_select)

        layout = QVBoxLayout(self)
        layout.addWidget(self._search)
        layout.addWidget(self._list)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self._select_btn)
        layout.addLayout(btn_row)

    def load_tags(self, tags: list[TagValue]) -> None:
        self._all_tags = tags
        self._apply_filter(self._search.text())

    def _apply_filter(self, text: str) -> None:
        self._list.clear()
        lower = text.lower()
        for tag in self._all_tags:
            if lower in tag.name.lower():
                item = QListWidgetItem(f"{tag.name}  [{tag.data_type}]")
                item.setData(Qt.UserRole, tag.name)
                self._list.addItem(item)

    def _on_double_click(self, item: QListWidgetItem) -> None:
        self.tag_selected.emit(item.data(Qt.UserRole))

    def _on_select(self) -> None:
        items = self._list.selectedItems()
        if items:
            self.tag_selected.emit(items[0].data(Qt.UserRole))
