from __future__ import annotations

# ─── Palette ──────────────────────────────────────────────────────────────────
BG_PRIMARY    = "#1a1d23"
BG_SECONDARY  = "#20242c"
BG_CARD       = "#252930"
BG_SURFACE    = "#2d3240"
BORDER        = "#383e50"
BORDER_FOCUS  = "#4d9de0"

TEXT_PRIMARY   = "#e8eaf0"
TEXT_SECONDARY = "#8b95a5"
TEXT_MUTED     = "#555f6d"

ACCENT_BLUE   = "#4d9de0"
ACCENT_GREEN  = "#3dd68c"
ACCENT_YELLOW = "#ffb703"
ACCENT_RED    = "#e63946"
ACCENT_ORANGE = "#fb8500"

# Fault row tint colors (background, foreground)
FAULT_MAJOR = ("#3a1a1c", "#f87171")
FAULT_MINOR = ("#2d2818", "#fbbf24")
FAULT_IO    = ("#1a2535", "#60a5fa")

# ─── Stylesheet ───────────────────────────────────────────────────────────────
STYLESHEET = """
/* ================================================================
   PLCTools — Dark Industrial Theme
   Principles: Clarity · Consistency · Conciseness · Feedback · Efficiency
   ================================================================ */

/* === Foundations === */
QMainWindow, QWidget {
    background-color: #1a1d23;
    color: #e8eaf0;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #141720;
    color: #b0b8c8;
    padding: 2px 4px;
    border-bottom: 1px solid #2d3240;
}
QMenuBar::item {
    padding: 4px 12px;
    border-radius: 3px;
}
QMenuBar::item:selected, QMenuBar::item:pressed {
    background-color: #2d3240;
    color: #e8eaf0;
}
QMenu {
    background-color: #252930;
    color: #c0c4d0;
    border: 1px solid #383e50;
    padding: 4px 0;
}
QMenu::item {
    padding: 7px 28px 7px 20px;
}
QMenu::item:selected {
    background-color: #35405a;
    color: #e8eaf0;
}
QMenu::separator {
    height: 1px;
    background: #383e50;
    margin: 4px 12px;
}

/* === Tabs === */
QTabWidget::pane {
    border: 1px solid #383e50;
    border-top: none;
    background: #1a1d23;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    background: #1e2230;
    color: #8b95a5;
    padding: 9px 22px;
    margin-right: 2px;
    border: 1px solid #383e50;
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    min-width: 90px;
    font-size: 12px;
    font-weight: 500;
}
QTabBar::tab:hover:!selected {
    background: #262c3a;
    color: #c0c4d0;
}
QTabBar::tab:selected {
    background: #1a1d23;
    color: #4d9de0;
    font-weight: bold;
    border-bottom-color: #1a1d23;
}

/* === Buttons — Base === */
QPushButton {
    background-color: #2d3240;
    color: #c0c4d0;
    border: 1px solid #383e50;
    border-radius: 4px;
    padding: 5px 16px;
    min-height: 28px;
    font-size: 13px;
    outline: none;
}
QPushButton:hover {
    background-color: #363d52;
    border-color: #4d9de0;
    color: #e8eaf0;
}
QPushButton:pressed {
    background-color: #3a4a6a;
    border-color: #4d9de0;
}
QPushButton:disabled {
    background-color: #20242c;
    color: #3d4560;
    border-color: #2a2f3e;
}

/* === Buttons — Semantic === */
QPushButton#connect_btn {
    background-color: #1e4976;
    color: #7cc8f8;
    border: 1px solid #2a6096;
    font-weight: bold;
}
QPushButton#connect_btn:hover {
    background-color: #265a8c;
    color: #a8daff;
    border-color: #4d9de0;
}
QPushButton#disconnect_btn {
    background-color: #3a1a1c;
    color: #f87171;
    border: 1px solid #5a2a2c;
    font-weight: bold;
}
QPushButton#disconnect_btn:hover {
    background-color: #4c2022;
    color: #fca5a5;
}
QPushButton#disconnect_btn:disabled {
    background-color: #20242c;
    color: #3d4560;
    border-color: #2a2f3e;
}
QPushButton#record_start_btn {
    background-color: #1e3a1e;
    color: #3dd68c;
    border: 1px solid #2a5a2a;
    font-weight: bold;
}
QPushButton#record_start_btn:hover {
    background-color: #254a28;
    color: #6be8a8;
    border-color: #3dd68c;
}
QPushButton#record_start_btn:disabled {
    background-color: #20242c;
    color: #3d4560;
    border-color: #2a2f3e;
}
QPushButton#record_stop_btn {
    background-color: #3a1a1c;
    color: #f87171;
    border: 1px solid #5a2a2c;
    font-weight: bold;
}
QPushButton#record_stop_btn:hover {
    background-color: #4c2022;
    color: #fca5a5;
}
QPushButton#record_stop_btn:disabled {
    background-color: #20242c;
    color: #3d4560;
    border-color: #2a2f3e;
}
QPushButton#refresh_btn {
    background-color: transparent;
    color: #8b95a5;
    border: 1px solid #383e50;
    padding: 4px 12px;
    min-height: 24px;
    font-size: 12px;
}
QPushButton#refresh_btn:hover {
    background-color: #2d3240;
    color: #4d9de0;
    border-color: #4d9de0;
}
QPushButton#demo_btn {
    background-color: #1a2d40;
    color: #60a5fa;
    border: 1px solid #1e4060;
    font-size: 12px;
}
QPushButton#demo_btn:hover {
    background-color: #1e3550;
    color: #93c5fd;
    border-color: #3a7ab8;
}

/* === Group Boxes (Cards) === */
QGroupBox {
    border: 1px solid #383e50;
    border-radius: 6px;
    margin-top: 20px;
    padding: 14px 10px 10px 10px;
    background-color: #1e2230;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: -9px;
    padding: 2px 8px;
    background-color: #1e2230;
    color: #4d9de0;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
}

/* === Tables === */
QTableWidget {
    background-color: #1e2128;
    alternate-background-color: #222630;
    gridline-color: #2d3240;
    border: 1px solid #383e50;
    border-radius: 4px;
    color: #c0c4d0;
    selection-background-color: #35405a;
    selection-color: #e8eaf0;
    outline: none;
}
QTableWidget::item {
    padding: 5px 10px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #35405a;
}
QHeaderView {
    background: #20242c;
}
QHeaderView::section {
    background-color: #20242c;
    color: #8b95a5;
    padding: 7px 10px;
    border: none;
    border-bottom: 2px solid #383e50;
    border-right: 1px solid #2d3240;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QHeaderView::section:last { border-right: none; }

/* === Tree Widget === */
QTreeWidget {
    background-color: #1e2128;
    alternate-background-color: #222630;
    border: 1px solid #383e50;
    border-radius: 4px;
    color: #c0c4d0;
    selection-background-color: #35405a;
    outline: none;
}
QTreeWidget::item {
    padding: 4px 6px;
}
QTreeWidget::item:selected {
    background-color: #35405a;
    color: #e8eaf0;
}
QTreeWidget::item:hover:!selected {
    background-color: #262b38;
}
QTreeWidget QHeaderView::section {
    background-color: #20242c;
    color: #8b95a5;
    padding: 6px 10px;
    border: none;
    border-bottom: 2px solid #383e50;
    border-right: 1px solid #2d3240;
    font-size: 11px;
    font-weight: bold;
}

/* === Input Fields === */
QLineEdit {
    background-color: #20242c;
    color: #e8eaf0;
    border: 1px solid #383e50;
    border-radius: 4px;
    padding: 5px 10px;
    min-height: 28px;
    selection-background-color: #35405a;
}
QLineEdit:focus { border-color: #4d9de0; background-color: #222830; }
QLineEdit:disabled { color: #555f6d; background-color: #1e2128; }

QSpinBox {
    background-color: #20242c;
    color: #e8eaf0;
    border: 1px solid #383e50;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 28px;
}
QSpinBox:focus { border-color: #4d9de0; }
QSpinBox::up-button, QSpinBox::down-button {
    background: #2d3240;
    border: none;
    border-left: 1px solid #383e50;
    width: 20px;
}
QSpinBox::up-button { border-bottom: 1px solid #383e50; border-top-right-radius: 4px; }
QSpinBox::down-button { border-bottom-right-radius: 4px; }
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #363d52; }

QComboBox {
    background-color: #20242c;
    color: #e8eaf0;
    border: 1px solid #383e50;
    border-radius: 4px;
    padding: 5px 10px;
    min-height: 28px;
}
QComboBox:focus { border-color: #4d9de0; }
QComboBox::drop-down {
    border: none;
    border-left: 1px solid #383e50;
    width: 24px;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}
QComboBox QAbstractItemView {
    background-color: #252930;
    color: #c0c4d0;
    border: 1px solid #4d9de0;
    selection-background-color: #35405a;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 6px 12px;
    min-height: 26px;
}

/* === Progress Bars === */
QProgressBar {
    background-color: #252930;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #8b95a5;
    min-height: 20px;
    font-size: 11px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #2a6aa8, stop:1 #4d9de0);
    border-radius: 4px;
}

/* === Scroll Bars === */
QScrollBar:vertical {
    background: #1a1d23; width: 8px; border: none; margin: 0;
}
QScrollBar::handle:vertical {
    background: #383e50; border-radius: 4px; min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #4d9de0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: #1a1d23; height: 8px; border: none; margin: 0;
}
QScrollBar::handle:horizontal {
    background: #383e50; border-radius: 4px; min-width: 24px;
}
QScrollBar::handle:horizontal:hover { background: #4d9de0; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* === Splitter === */
QSplitter::handle { background: #2d3240; }
QSplitter::handle:hover { background: #4d9de0; }
QSplitter::handle:horizontal { width: 3px; }
QSplitter::handle:vertical { height: 3px; }

/* === Status Bar === */
QStatusBar {
    background-color: #141720;
    color: #8b95a5;
    border-top: 1px solid #2d3240;
    font-size: 11px;
    padding: 0 8px;
    min-height: 22px;
}

/* === Labels === */
QLabel { color: #c0c4d0; background: transparent; }

/* === Dialogs === */
QDialog { background-color: #1a1d23; }
QDialogButtonBox QPushButton { min-width: 80px; }

/* === Tooltips === */
QToolTip {
    background-color: #252930;
    color: #e8eaf0;
    border: 1px solid #4d9de0;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
}

/* === List Widget === */
QListWidget {
    background-color: #1e2128;
    alternate-background-color: #222630;
    color: #c0c4d0;
    border: 1px solid #383e50;
    border-radius: 4px;
    outline: none;
}
QListWidget::item { padding: 5px 10px; }
QListWidget::item:selected { background-color: #35405a; color: #e8eaf0; }
QListWidget::item:hover:!selected { background-color: #262b38; }
"""
