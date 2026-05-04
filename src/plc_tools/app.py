from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from plc_tools.gui.main_window import MainWindow
from plc_tools.gui.theme import STYLESHEET


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("PLC Tools")
    app.setOrganizationName("PLCTools")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
