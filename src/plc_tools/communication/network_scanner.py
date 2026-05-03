from __future__ import annotations

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

try:
    from pycomm3 import CIPDriver

    _PYCOMM3_AVAILABLE = True
except ImportError:
    _PYCOMM3_AVAILABLE = False

CIP_PORT = 44818
SCAN_TIMEOUT = 1.0


@dataclass
class ScanResult:
    ip_address: str
    hostname: str
    port_open: bool
    product_name: str = ""
    vendor: str = ""
    serial: str = ""

    @property
    def is_plc(self) -> bool:
        return self.port_open


def _resolve_hostname(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ""


def _probe_cip(ip: str) -> tuple[str, str, str]:
    if not _PYCOMM3_AVAILABLE:
        return "", "", ""
    try:
        with CIPDriver(ip) as plc:
            info = plc.info
            return (
                info.get("product_name", ""),
                info.get("vendor", ""),
                info.get("serial", ""),
            )
    except Exception:
        return "", "", ""


def _check_host(ip: str) -> ScanResult:
    hostname = _resolve_hostname(ip)
    try:
        with socket.create_connection((ip, CIP_PORT), timeout=SCAN_TIMEOUT):
            port_open = True
    except OSError:
        port_open = False

    product_name = vendor = serial = ""
    if port_open:
        product_name, vendor, serial = _probe_cip(ip)

    return ScanResult(
        ip_address=ip,
        hostname=hostname,
        port_open=port_open,
        product_name=product_name,
        vendor=vendor,
        serial=serial,
    )


def _subnet_hosts(subnet: str) -> list[str]:
    parts = subnet.split(".")
    if len(parts) != 4:
        return []
    base = ".".join(parts[:3])
    return [f"{base}.{i}" for i in range(1, 255)]


class NetworkScanner:
    def __init__(self, max_workers: int = 64) -> None:
        self._max_workers = max_workers
        self._cancel = threading.Event()

    def scan_subnet(
        self,
        subnet: str,
        progress_callback: "callable[[int, int], None] | None" = None,
    ) -> list[ScanResult]:
        hosts = _subnet_hosts(subnet)
        results: list[ScanResult] = []
        self._cancel.clear()

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = {executor.submit(_check_host, ip): ip for ip in hosts}
            completed = 0
            for future in as_completed(futures):
                if self._cancel.is_set():
                    break
                completed += 1
                result = future.result()
                if result.port_open:
                    results.append(result)
                if progress_callback:
                    progress_callback(completed, len(hosts))

        return results

    def scan_single(self, ip: str) -> ScanResult:
        return _check_host(ip)

    def cancel(self) -> None:
        self._cancel.set()
