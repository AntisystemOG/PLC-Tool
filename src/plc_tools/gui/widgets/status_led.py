from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QSizePolicy, QWidget

_COLORS = {
    "green": ("#00cc44", "#004d1a"),
    "red": ("#cc0000", "#4d0000"),
    "yellow": ("#cccc00", "#4d4d00"),
    "gray": ("#808080", "#303030"),
}


class StatusLed(QWidget):
    def __init__(self, color: str = "gray", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self.setFixedSize(18, 18)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_color(self, color: str) -> None:
        if color != self._color:
            self._color = color
            self.update()

    def set_green(self) -> None:
        self.set_color("green")

    def set_red(self) -> None:
        self.set_color("red")

    def set_yellow(self) -> None:
        self.set_color("yellow")

    def set_gray(self) -> None:
        self.set_color("gray")

    def paintEvent(self, event: object) -> None:
        light, dark = _COLORS.get(self._color, _COLORS["gray"])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx, cy, r = self.width() / 2, self.height() / 2, min(self.width(), self.height()) / 2 - 1
        gradient = QRadialGradient(cx * 0.7, cy * 0.7, r)
        gradient.setColorAt(0.0, QColor(light).lighter(150))
        gradient.setColorAt(0.5, QColor(light))
        gradient.setColorAt(1.0, QColor(dark))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
