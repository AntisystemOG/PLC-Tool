from __future__ import annotations

from PySide6.QtCore import QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from plc_tools.communication.connection_manager import ConnectionManager
from plc_tools.communication.models import ConnectionConfig
from plc_tools.communication.project_manager import ProjectManager
from plc_tools.gui.connect_dialog import ConnectDialog
from plc_tools.gui.tabs.diagnostics import DiagnosticsTab
from plc_tools.gui.tabs.fault_log import FaultLogTab
from plc_tools.gui.tabs.io_status import IOStatusTab
from plc_tools.gui.tabs.program_view import ProgramViewTab
from plc_tools.gui.tabs.tag_list import TagListTab
from plc_tools.gui.tabs.tag_monitor import TagMonitorTab
from plc_tools.gui.widgets.connection_bar import ConnectionBar
from plc_tools.gui.widgets.recording_bar import RecordingBar
from plc_tools.polling.poller import Poller
from plc_tools.recording.recorder import DataRecorder
from plc_tools.reports.generator import ReportGenerator


class _ConnectWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, manager: ConnectionManager, config: ConnectionConfig) -> None:
        super().__init__()
        self._manager = manager
        self._config = config

    def run(self) -> None:
        try:
            ok = self._manager.connect(self._config)
            self.finished.emit(ok, "" if ok else "Connection refused")
        except Exception as exc:
            self.finished.emit(False, str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PLC Tools")
        self.setMinimumSize(900, 620)

        self._conn_mgr = ConnectionManager()
        self._proj_mgr = ProjectManager()
        self._poller = Poller(self._conn_mgr)
        self._report_gen = ReportGenerator()
        self._recorder = DataRecorder()
        self._recorder.on_auto_stopped = self._on_recording_auto_stopped
        self._worker: _ConnectWorker | None = None

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_tick)

        self._record_tick_timer = QTimer(self)
        self._record_tick_timer.setInterval(1000)
        self._record_tick_timer.timeout.connect(self._update_recording_status)

        self._build_ui()
        self._build_menu()
        self._update_ui_disconnected()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        self._conn_bar = ConnectionBar()
        self._conn_bar.disconnect_requested.connect(self._do_disconnect)
        layout.addWidget(self._conn_bar)

        self._rec_bar = RecordingBar()
        self._rec_bar.start_requested.connect(self._start_recording)
        self._rec_bar.stop_requested.connect(self._stop_recording)
        self._rec_bar.set_connected(False)

        self._tabs = QTabWidget()
        self._tab_diag = DiagnosticsTab()
        self._tab_fault = FaultLogTab()
        self._tab_io = IOStatusTab()
        self._tab_programs = ProgramViewTab()
        self._tab_tags = TagListTab()
        self._tab_monitor = TagMonitorTab()

        self._tabs.addTab(self._tab_diag, "Diagnostics")
        self._tabs.addTab(self._tab_fault, "Fault Log")
        self._tabs.addTab(self._tab_io, "I/O Status")
        self._tabs.addTab(self._tab_programs, "Programs")
        self._tabs.addTab(self._tab_tags, "Tag List")
        self._tabs.addTab(self._tab_monitor, "Tag Monitor")
        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs)
        layout.addWidget(self._rec_bar)

        self._tab_diag._refresh_btn.clicked.connect(self._load_diagnostics)
        self._tab_fault._refresh_btn.clicked.connect(self._load_faults)
        self._tab_io._refresh_btn.clicked.connect(self._load_io)
        self._tab_programs._refresh_btn.clicked.connect(self._load_programs)
        self._tab_tags._refresh_btn.clicked.connect(self._load_tags)

        self._tab_monitor.poll_interval_changed.connect(self._on_poll_interval_changed)
        self._tab_monitor.tag_added.connect(self._poller.add_tag)
        self._tab_monitor.tag_removed.connect(self._poller.remove_tag)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

    def _build_menu(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("&File")
        file_menu.addAction("&Connect…", self._do_connect)
        file_menu.addAction("&Disconnect", self._do_disconnect)
        file_menu.addSeparator()
        file_menu.addAction("Open &L5X…", self._open_l5x)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        reports_menu = mb.addMenu("&Reports")
        reports_menu.addAction("Export Fault Log…", self._export_faults)
        reports_menu.addAction("Export Tag List…", self._export_tags)

        tools_menu = mb.addMenu("&Tools")
        tools_menu.addAction("Scan Network…", self._scan_network)

    def _do_connect(self) -> None:
        dlg = ConnectDialog(self._proj_mgr, self)
        if dlg.exec() and dlg.config:
            config = dlg.config
            self._conn_bar.set_connecting(config.ip_address)
            self.setEnabled(False)
            self._worker = _ConnectWorker(self._conn_mgr, config)
            self._worker.finished.connect(self._on_connect_finished)
            self._worker.start()

    @Slot(bool, str)
    def _on_connect_finished(self, ok: bool, error: str) -> None:
        self.setEnabled(True)
        if ok:
            cfg = self._conn_mgr.config
            self._conn_bar.set_connected(cfg.ip_address, cfg.name)
            self._status_bar.showMessage(f"Connected to {cfg.name}", 4000)
            self._update_ui_connected()
            self._load_all()
        else:
            self._conn_bar.set_error(error)
            self._status_bar.showMessage(f"Connection failed: {error}", 6000)

    def _do_disconnect(self) -> None:
        self._poll_timer.stop()
        self._conn_mgr.disconnect()
        self._conn_bar.set_disconnected()
        self._update_ui_disconnected()
        self._status_bar.showMessage("Disconnected", 3000)

    def _update_ui_connected(self) -> None:
        self._tabs.setEnabled(True)
        self._poll_timer.start(self._tab_monitor._interval_spin.value())
        self._rec_bar.set_connected(True)

    def _update_ui_disconnected(self) -> None:
        self._stop_recording()
        self._rec_bar.set_connected(False)
        for tab in (self._tab_diag, self._tab_fault, self._tab_io,
                    self._tab_programs, self._tab_tags, self._tab_monitor):
            tab.clear()

    def _load_all(self) -> None:
        self._load_diagnostics()
        self._load_faults()
        self._load_io()
        self._load_programs()
        self._load_tags()

    def _load_diagnostics(self) -> None:
        if not self._conn_mgr.is_connected:
            return
        info = self._conn_mgr.driver.get_controller_info()
        self._tab_diag.load_info(info)

    def _load_faults(self) -> None:
        if not self._conn_mgr.is_connected:
            return
        faults = self._conn_mgr.driver.get_fault_log()
        self._tab_fault.load_faults(faults)

    def _load_io(self) -> None:
        if not self._conn_mgr.is_connected:
            return
        modules = self._conn_mgr.driver.get_io_modules()
        self._tab_io.load_modules(modules)

    def _load_programs(self) -> None:
        if not self._conn_mgr.is_connected:
            return
        programs = self._conn_mgr.driver.get_programs()
        self._tab_programs.load_programs(programs)

    def _load_tags(self) -> None:
        if not self._conn_mgr.is_connected:
            return
        tags = self._conn_mgr.driver.get_tag_list()
        self._tab_tags.load_tags(tags)
        self._tab_monitor.set_available_tags(tags)

    def _on_tab_changed(self, index: int) -> None:
        pass

    def _poll_tick(self) -> None:
        if not self._conn_mgr.is_connected:
            return
        tags = self._tab_monitor.watched_tags
        if tags:
            values = self._conn_mgr.driver.read_tags(tags)
            self._tab_monitor.update_values(values)
            if self._recorder.is_active:
                self._recorder.record(values)

    def _start_recording(self, path: str) -> None:
        self._recorder.start(path)
        self._rec_bar.set_recording()
        self._record_tick_timer.start()
        self._status_bar.showMessage(f"Recording to {path}", 4000)

    def _stop_recording(self) -> None:
        if self._recorder.is_active:
            self._recorder.stop()
            self._status_bar.showMessage(
                f"Recording saved — {self._recorder.sample_count:,} samples", 5000
            )
        self._record_tick_timer.stop()
        self._rec_bar.set_idle()

    def _on_recording_auto_stopped(self) -> None:
        self._record_tick_timer.stop()
        self._rec_bar.set_idle()
        self._status_bar.showMessage(
            f"Recording complete (12 hours) — {self._recorder.sample_count:,} samples saved", 6000
        )

    def _update_recording_status(self) -> None:
        if self._recorder.is_active:
            self._rec_bar.update_status(
                self._recorder.elapsed_seconds,
                self._recorder.remaining_seconds,
                self._recorder.sample_count,
            )

    def _on_poll_interval_changed(self, ms: int) -> None:
        if self._poll_timer.isActive():
            self._poll_timer.setInterval(ms)

    def _open_l5x(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open L5X File", "", "L5X Files (*.L5X *.l5x)")
        if not path:
            return
        try:
            from plc_tools.communication.l5x_parser import parse_l5x
            project = parse_l5x(path)
            programs = [
                __import__("plc_tools.communication.models", fromlist=["ProgramInfo"]).ProgramInfo(
                    name=p.name,
                    program_type="Normal",
                    routines=[
                        __import__("plc_tools.communication.models", fromlist=["RoutineInfo"]).RoutineInfo(
                            name=r.name, routine_type=r.routine_type
                        )
                        for r in p.routines
                    ],
                )
                for p in project.programs
            ]
            self._tab_programs.load_programs(programs)
            self._tabs.setCurrentWidget(self._tab_programs)
            self._status_bar.showMessage(f"Loaded {path}", 4000)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to parse L5X:\n{exc}")

    def _export_faults(self) -> None:
        if not self._conn_mgr.is_connected:
            QMessageBox.information(self, "Not Connected", "Connect to a PLC first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Fault Log", "fault_log.txt", "Text (*.txt);;CSV (*.csv)")
        if not path:
            return
        faults = self._conn_mgr.driver.get_fault_log()
        self._report_gen.export_fault_log(faults, path)
        self._status_bar.showMessage(f"Exported to {path}", 4000)

    def _export_tags(self) -> None:
        if not self._conn_mgr.is_connected:
            QMessageBox.information(self, "Not Connected", "Connect to a PLC first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Tag List", "tags.csv", "CSV (*.csv);;Text (*.txt)")
        if not path:
            return
        tags = self._conn_mgr.driver.get_tag_list()
        self._report_gen.export_tag_list(tags, path)
        self._status_bar.showMessage(f"Exported to {path}", 4000)

    def _scan_network(self) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QInputDialog, QProgressDialog
        subnet, ok = QInputDialog.getText(self, "Scan Network", "Enter subnet (e.g. 192.168.1.0):", text="192.168.1.0")
        if not ok or not subnet:
            return
        from plc_tools.communication.network_scanner import NetworkScanner
        scanner = NetworkScanner()
        progress = QProgressDialog("Scanning network…", "Cancel", 0, 254, self)
        progress.setWindowTitle("Network Scan")
        progress.show()
        results = []

        def _progress(done: int, total: int) -> None:
            progress.setValue(done)
            if progress.wasCanceled():
                scanner.cancel()

        results = scanner.scan_subnet(subnet, _progress)
        progress.close()

        if not results:
            QMessageBox.information(self, "Scan Complete", "No PLCs found on the subnet.")
            return

        lines = "\n".join(f"{r.ip_address}  {r.product_name}  {r.vendor}" for r in results)
        QMessageBox.information(self, f"Found {len(results)} device(s)", lines)

    def closeEvent(self, event: object) -> None:
        self._poll_timer.stop()
        self._stop_recording()
        self._conn_mgr.disconnect()
        super().closeEvent(event)
