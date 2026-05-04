from __future__ import annotations

from typing import Any

from .base_driver import BasePLCDriver
from .models import (
    ConnectionConfig,
    ControllerInfo,
    FaultEntry,
    IOChannel,
    IOModule,
    MICRO800_SPECS,
    PLCType,
    ProgramInfo,
    RoutineInfo,
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
        self._model_type: PLCType = config.plc_type

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
        # CIPDriver does not support Logix-style symbol table enumeration.
        # Micro800 exposes tags via CIP Symbol Object (class 0x6B) but pycomm3
        # does not decode the full symbol table from CIPDriver — only tag names
        # known in advance can be read. Return empty; caller handles gracefully.
        return []

    def get_programs(self) -> list[ProgramInfo]:
        # Micro800 CCW projects have one implicit task. CIPDriver info dict
        # provides the controller name which we use as the program name.
        try:
            prog_name = self._plc.info.get("name", "Micro800Program")
        except Exception:
            prog_name = "Micro800Program"
        return [
            ProgramInfo(
                name=prog_name,
                program_type="Normal",
                routines=[RoutineInfo("MainRoutine", "ST")],
            )
        ]

    def get_io_modules(self) -> list[IOModule]:
        specs = MICRO800_SPECS.get(self._model_type, MICRO800_SPECS[PLCType.MICRO800])
        catalog_prefix = specs["catalog"]
        modules: list[IOModule] = []

        # Slot 0 — onboard I/O is always present on every Micro800 model
        onboard_channels: list[IOChannel] = (
            [IOChannel(i, f"_IO_EM_DI_{i:02d}", False, True)  for i in range(specs["di"])]
            + [IOChannel(i, f"_IO_EM_DO_{i:02d}", False, False) for i in range(specs["do"])]
            + [IOChannel(i, f"_IO_EM_AI_{i:02d}", 0.0, True)  for i in range(specs["ai"])]
        )
        modules.append(IOModule(
            slot=0,
            name=f"Micro800 Onboard I/O ({catalog_prefix})",
            vendor="Allen-Bradley",
            catalog=catalog_prefix,
            status="Running" if self._connected else "Unknown",
            channels=onboard_channels,
        ))

        # Attempt to detect plug-in modules via CIP Identity Object walk.
        # Micro800 expansion modules appear at device instances 2+ in the CIP object model.
        if hasattr(self._plc, "generic_message"):
            for instance in range(2, specs["expansion"] + 2):
                try:
                    result = self._plc.generic_message(
                        service=0x0E,     # Get_Attribute_Single
                        class_code=0x01,  # Identity Object
                        instance=instance,
                        attribute=7,      # Product Name
                        connected=False,
                        unconnected_send=True,
                        route_path=True,
                    )
                    if result and not result.error:
                        mod_name = str(result.value) if result.value else f"Expansion Module (slot {instance - 1})"
                        modules.append(IOModule(
                            slot=instance - 1,
                            name=mod_name,
                            vendor="Allen-Bradley",
                            catalog="",
                            status="Running",
                            channels=[],
                        ))
                except Exception:
                    break   # No more modules at higher instances

        return modules

    def get_fault_log(self) -> list[FaultEntry]:
        # Micro800 exposes a Fault Table at CIP class 0x8E. The byte layout is
        # firmware-version-specific and not publicly documented, so we probe for
        # its presence but cannot reliably decode entries without that information.
        # Return empty; a future enhancement can decode entries once byte offsets
        # are confirmed from firmware documentation.
        return []

    def get_controller_info(self) -> ControllerInfo:
        specs = MICRO800_SPECS.get(self._model_type, MICRO800_SPECS[PLCType.MICRO800])
        catalog_prefix = specs["catalog"]
        try:
            info = self._plc.info
            name = info.get("name") or info.get("product_name", "Micro800")
            serial_raw = info.get("serial", 0)
            serial = f"{serial_raw:08X}" if isinstance(serial_raw, int) else str(serial_raw)
            rev = info.get("revision", {})
            if isinstance(rev, dict):
                firmware = f"{rev.get('major', '?')}.{rev.get('minor', 0):03d}"
            else:
                firmware = str(rev)
            catalog = info.get("product_name", catalog_prefix)
            vendor = info.get("vendor", "Allen-Bradley")
        except Exception:
            name = "Micro800"
            serial = ""
            firmware = ""
            catalog = catalog_prefix
            vendor = "Allen-Bradley"

        return ControllerInfo(
            name=name,
            serial_number=serial,
            firmware=firmware,
            catalog=catalog,
            vendor=vendor,
            keyswitch="Unknown",
            status="Running" if self._connected else "Unknown",
            programs=self.get_programs(),
        )
