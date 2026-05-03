from __future__ import annotations

from typing import Any

from .base_driver import BasePLCDriver
from .models import (
    ConnectionConfig,
    ControllerInfo,
    FaultEntry,
    IOModule,
    ProgramInfo,
    TagValue,
)

try:
    from pycomm3 import CIPDriver as _CIPDriver

    _PYCOMM3_AVAILABLE = True
except ImportError:
    _PYCOMM3_AVAILABLE = False


class Micro800Driver(BasePLCDriver):
    def __init__(self, config: ConnectionConfig) -> None:
        super().__init__(config)
        self._plc: Any = None

    def connect(self) -> bool:
        if not _PYCOMM3_AVAILABLE:
            raise RuntimeError("pycomm3 is not installed")
        self._plc = _CIPDriver(self.config.ip_address)
        try:
            self._plc.open()
            self._connected = True
            return True
        except Exception:
            self._connected = False
            self._plc = None
            return False

    def disconnect(self) -> None:
        if self._plc is not None:
            try:
                self._plc.close()
            except Exception:
                pass
            self._plc = None
        self._connected = False

    def read_tag(self, tag_name: str) -> TagValue:
        try:
            result = self._plc.read(tag_name)
            if result.error:
                return TagValue(name=tag_name, value=None, data_type="UNKNOWN", error=str(result.error))
            return TagValue(name=tag_name, value=result.value, data_type=str(result.type or "UNKNOWN"))
        except Exception as exc:
            return TagValue(name=tag_name, value=None, data_type="UNKNOWN", error=str(exc))

    def read_tags(self, tag_names: list[str]) -> list[TagValue]:
        return [self.read_tag(n) for n in tag_names]

    def write_tag(self, tag_name: str, value: Any) -> bool:
        try:
            result = self._plc.write((tag_name, value))
            return result.error is None
        except Exception:
            return False

    def get_tag_list(self) -> list[TagValue]:
        return []

    def get_programs(self) -> list[ProgramInfo]:
        return []

    def get_io_modules(self) -> list[IOModule]:
        return []

    def get_fault_log(self) -> list[FaultEntry]:
        return []

    def get_controller_info(self) -> ControllerInfo:
        return ControllerInfo(
            name="Micro800",
            serial_number="",
            firmware="",
            catalog="",
            vendor="Allen-Bradley",
            keyswitch="Unknown",
            status="Unknown",
        )
