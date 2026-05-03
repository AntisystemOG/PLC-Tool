from __future__ import annotations

from datetime import datetime
from typing import Any

from .base_driver import BasePLCDriver
from .models import (
    ConnectionConfig,
    ControllerInfo,
    FaultEntry,
    FaultType,
    IOModule,
    ProgramInfo,
    RoutineInfo,
    TagValue,
)

try:
    from pycomm3 import LogixDriver as _LogixDriver
    from pycomm3.exceptions import CommError, RequestError

    _PYCOMM3_AVAILABLE = True
except ImportError:
    _PYCOMM3_AVAILABLE = False


class LogixDriver(BasePLCDriver):
    def __init__(self, config: ConnectionConfig) -> None:
        super().__init__(config)
        self._plc: Any = None

    def connect(self) -> bool:
        if not _PYCOMM3_AVAILABLE:
            raise RuntimeError("pycomm3 is not installed")
        path = f"{self.config.ip_address}/{self.config.slot}"
        self._plc = _LogixDriver(path, init_tags=False, init_info=True)
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

    def _make_tag_value(self, tag: Any) -> TagValue:
        if tag.error:
            return TagValue(name=tag.tag, value=None, data_type="UNKNOWN", error=str(tag.error))
        dtype = str(tag.type) if tag.type else "UNKNOWN"
        return TagValue(name=tag.tag, value=tag.value, data_type=dtype)

    def read_tag(self, tag_name: str) -> TagValue:
        try:
            result = self._plc.read(tag_name)
            return self._make_tag_value(result)
        except Exception as exc:
            return TagValue(name=tag_name, value=None, data_type="UNKNOWN", error=str(exc))

    def read_tags(self, tag_names: list[str]) -> list[TagValue]:
        try:
            results = self._plc.read(*tag_names)
            if not isinstance(results, (list, tuple)):
                results = [results]
            return [self._make_tag_value(r) for r in results]
        except Exception as exc:
            return [TagValue(name=n, value=None, data_type="UNKNOWN", error=str(exc)) for n in tag_names]

    def write_tag(self, tag_name: str, value: Any) -> bool:
        try:
            result = self._plc.write((tag_name, value))
            return result.error is None
        except Exception:
            return False

    def get_tag_list(self) -> list[TagValue]:
        try:
            self._plc.get_tag_list(program="*")
            tags = []
            for name, attrs in self._plc.tags.items():
                dtype = str(attrs.get("data_type", "UNKNOWN"))
                tags.append(TagValue(name=name, value=None, data_type=dtype))
            return tags
        except Exception:
            return []

    def get_programs(self) -> list[ProgramInfo]:
        try:
            programs = []
            info = self._plc.info
            for prog_name in info.get("programs", {}).keys():
                prog_info = info["programs"][prog_name]
                routines = [
                    RoutineInfo(name=r, routine_type=prog_info.get("routines", {}).get(r, {}).get("type", "LAD"))
                    for r in prog_info.get("routines", {}).keys()
                ]
                programs.append(ProgramInfo(name=prog_name, program_type="Normal", routines=routines))
            return programs
        except Exception:
            return []

    def get_io_modules(self) -> list[IOModule]:
        try:
            modules = []
            for slot, mod in enumerate(self._plc.info.get("modules", {}).values()):
                modules.append(
                    IOModule(
                        slot=slot,
                        name=mod.get("product_name", ""),
                        vendor=mod.get("vendor", ""),
                        catalog=mod.get("catalog", ""),
                        status=mod.get("status", "Unknown"),
                    )
                )
            return modules
        except Exception:
            return []

    def get_fault_log(self) -> list[FaultEntry]:
        try:
            faults = []
            raw = self._plc.get_plc_info()
            for entry in raw.get("faults", []):
                faults.append(
                    FaultEntry(
                        code=entry.get("code", 0),
                        description=entry.get("description", ""),
                        timestamp=entry.get("timestamp", datetime.now()),
                        fault_type=FaultType(entry.get("type", "minor")),
                    )
                )
            return faults
        except Exception:
            return []

    def get_controller_info(self) -> ControllerInfo:
        try:
            info = self._plc.info
            return ControllerInfo(
                name=info.get("name", ""),
                serial_number=info.get("serial", ""),
                firmware=info.get("revision", {}).get("major", "?"),
                catalog=info.get("product_name", ""),
                vendor=info.get("vendor", "Allen-Bradley"),
                keyswitch=info.get("keyswitch", "Unknown"),
                status=info.get("status", "Unknown"),
                programs=self.get_programs(),
            )
        except Exception:
            return ControllerInfo(
                name="Unknown",
                serial_number="",
                firmware="",
                catalog="",
                vendor="Allen-Bradley",
                keyswitch="Unknown",
                status="Unknown",
            )
