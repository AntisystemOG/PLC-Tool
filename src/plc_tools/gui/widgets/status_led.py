from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QSizePolicy, QWidget

_COLORS = {
    "green":  ("#3dd68c", "#0f6035"),
    "red":    ("#e63946", "#6b0f14"),
    "yellow": ("#ffb703", "#7a5500"),
    "gray":   ("#6b7280", "#2a2d35"),
}


class StatusLed(QWidget):
    def __init__(self, color: str = "gray", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self.setFixedSize(12, 12)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_color(self, color: str) -> None:
        if color != self._color:
            self._color = color
            self.update()

    def set_green(self)  -> None: self.set_color("green")
    def set_red(self)    -> None: self.set_color("red")
    def set_yellow(self) -> None: self.set_color("yellow")
    def set_gray(self)   -> None: self.set_color("gray")

    def paintEvent(self, event: object) -> None:
        light, dark = _COLORS.get(self._color, _COLORS["gray"])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width()  / 2
        cy = self.height() / 2
        r  = min(self.width(), self.height()) / 2 - 1
        gradient = QRadialGradient(cx * 0.65, cy * 0.65, r)
        gradient.setColorAt(0.0, QColor(light).lighter(160))
        gradient.setColorAt(0.45, QColor(light))
        gradient.setColorAt(1.0,  QColor(dark))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
