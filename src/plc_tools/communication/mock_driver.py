from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

from .base_driver import BasePLCDriver
from .models import (
    ConnectionConfig,
    ControllerInfo,
    FaultEntry,
    FaultType,
    IOChannel,
    IOModule,
    PLCType,
    ProgramInfo,
    RoutineInfo,
    TagValue,
)

# Flat CCW-style global variable names (no Program: prefix — Micro800 uses global scope)
_MOCK_TAGS: dict[str, tuple[Any, str]] = {
    # --- Controller globals ---
    "HeartBeat":              (0,      "DINT"),
    "SystemReady":            (True,   "BOOL"),
    "AlarmActive":            (False,  "BOOL"),
    "AlarmCode":              (0,      "UINT"),
    "CycleCount":             (4712,   "DINT"),
    "BatchCount":             (94,     "DINT"),
    "RunMode":                (1,      "USINT"),   # 0=Stop 1=Run 2=Fault

    # --- Conveyor ---
    "Conveyor_Enable":        (True,   "BOOL"),
    "Conveyor_Running":       (True,   "BOOL"),
    "Conveyor_Fault":         (False,  "BOOL"),
    "Conveyor_SpeedCmd":      (65.0,   "REAL"),    # % of full speed
    "Conveyor_SpeedFbk":      (64.7,   "REAL"),
    "Conveyor_AmpsAI":        (3.2,    "REAL"),    # motor current (A)

    # --- Fill station ---
    "FillStation_Enable":     (True,   "BOOL"),
    "FillStation_Filling":    (False,  "BOOL"),
    "FillStation_Complete":   (True,   "BOOL"),
    "FillStation_Fault":      (False,  "BOOL"),
    "FillValve_Open":         (False,  "BOOL"),
    "FillWeight_AI":          (0.0,    "REAL"),    # kg
    "FillSetpoint":           (1.250,  "REAL"),    # kg
    "FillTolerance":          (0.025,  "REAL"),    # kg

    # --- Digital sensors ---
    "Sensor_BottlePresent":   (True,   "BOOL"),
    "Sensor_ConvFull":        (False,  "BOOL"),
    "Sensor_ConvEmpty":       (False,  "BOOL"),
    "Sensor_DoorClosed":      (True,   "BOOL"),
    "Sensor_EStop":           (True,   "BOOL"),    # True = OK (NC contact logic)

    # --- Onboard AI raw counts (0–32767) ---
    "_IO_EM_AI_00":           (16384,  "INT"),     # conveyor speed feedback
    "_IO_EM_AI_01":           (8200,   "INT"),     # fill weight
    "_IO_EM_AI_02":           (3100,   "INT"),     # motor current
    "_IO_EM_AI_03":           (0,      "INT"),     # spare

    # --- Timer accumulator values (ms) ---
    "FillTimer_ACC":          (0,      "DINT"),
    "FillTimer_PRE":          (3000,   "DINT"),    # 3 s fill time preset
    "ConvTimer_ACC":          (0,      "DINT"),
}


class MockDriver(BasePLCDriver):
    def __init__(self, config: ConnectionConfig | None = None) -> None:
        if config is None:
            config = ConnectionConfig(ip_address="127.0.0.1", plc_type=PLCType.MOCK, name="Demo Micro850")
        super().__init__(config)
        self._tag_store: dict[str, tuple[Any, str]] = dict(_MOCK_TAGS)
        self._cycle = 0

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def read_tag(self, tag_name: str) -> TagValue:
        self._cycle += 1
        if tag_name not in self._tag_store:
            return TagValue(name=tag_name, value=None, data_type="UNKNOWN", error="Tag not found")
        value, dtype = self._tag_store[tag_name]
        if dtype == "REAL":
            magnitude = max(abs(value), 0.1)
            value = round(value + random.uniform(-0.02 * magnitude, 0.02 * magnitude), 3)
        elif tag_name == "HeartBeat":
            value = self._cycle % 32767
            self._tag_store[tag_name] = (value, dtype)
        elif tag_name.startswith("_IO_EM_AI_"):
            value = max(0, min(32767, value + random.randint(-30, 30)))
            self._tag_store[tag_name] = (value, dtype)
        return TagValue(name=tag_name, value=value, data_type=dtype)

    def read_tags(self, tag_names: list[str]) -> list[TagValue]:
        return [self.read_tag(n) for n in tag_names]

    def write_tag(self, tag_name: str, value: Any) -> bool:
        if tag_name in self._tag_store:
            _, dtype = self._tag_store[tag_name]
            self._tag_store[tag_name] = (value, dtype)
            return True
        return False

    def get_tag_list(self) -> list[TagValue]:
        return [TagValue(name=k, value=v, data_type=dt) for k, (v, dt) in self._tag_store.items()]

    def get_programs(self) -> list[ProgramInfo]:
        return [
            ProgramInfo(
                name="FillingLine",
                program_type="Normal",
                routines=[
                    RoutineInfo("MainRoutine",        "ST"),
                    RoutineInfo("ConveyorControl",    "FBD"),
                    RoutineInfo("FillStationControl", "ST"),
                    RoutineInfo("AlarmHandling",      "ST"),
                    RoutineInfo("SafetyChecks",       "ST"),
                ],
            )
        ]

    def get_io_modules(self) -> list[IOModule]:
        return [
            IOModule(
                slot=0,
                name="Micro850 Onboard I/O",
                vendor="Allen-Bradley",
                catalog="2080-LC50-48QWB",
                status="Running",
                channels=(
                    [IOChannel(i, f"_IO_EM_DI_{i:02d}", bool(random.randint(0, 1)), True)
                     for i in range(28)]
                    + [IOChannel(i, f"_IO_EM_DO_{i:02d}", bool(random.randint(0, 1)), False)
                       for i in range(20)]
                    + [IOChannel(i, f"_IO_EM_AI_{i:02d}", round(random.uniform(0, 32767), 0), True)
                       for i in range(4)]
                ),
            ),
            IOModule(
                slot=1,
                name="2-Ch Analog Output Plug-In",
                vendor="Allen-Bradley",
                catalog="2080-OF2",
                status="Running",
                channels=[
                    IOChannel(0, "_IO_P1_AO_00", round(random.uniform(0, 32767), 0), False),
                    IOChannel(1, "_IO_P1_AO_01", round(random.uniform(0, 32767), 0), False),
                ],
            ),
            IOModule(
                slot=2,
                name="High-Speed Counter / Serial Plug-In",
                vendor="Allen-Bradley",
                catalog="2080-SERIALISOL",
                status="Running",
                channels=[
                    IOChannel(0, "_IO_P2_DI_00", bool(random.randint(0, 1)), True),
                    IOChannel(1, "_IO_P2_DI_01", bool(random.randint(0, 1)), True),
                ],
            ),
        ]

    def get_fault_log(self) -> list[FaultEntry]:
        now = datetime.now()
        return [
            FaultEntry(
                code=0x0083,
                description="Minor fault: Output overload on _IO_EM_DO_07 (FillValve_Open)",
                timestamp=now - timedelta(minutes=47),
                fault_type=FaultType.MINOR,
                program="FillingLine",
            ),
            FaultEntry(
                code=0x0041,
                description="Major fault: Watchdog timeout — FillingLine task exceeded 20 ms scan time",
                timestamp=now - timedelta(hours=6, minutes=12),
                fault_type=FaultType.MAJOR,
                program="FillingLine",
            ),
            FaultEntry(
                code=0x0010,
                description="I/O fault: Plug-in module slot 2 communication loss (2080-SERIALISOL)",
                timestamp=now - timedelta(days=2, hours=3),
                fault_type=FaultType.IO,
                program="",
            ),
        ]

    def get_controller_info(self) -> ControllerInfo:
        return ControllerInfo(
            name="Micro850_FillingLine",
            serial_number="00A3F712",
            firmware="21.011",
            catalog="2080-LC50-48QWB",
            vendor="Allen-Bradley",
            keyswitch="Run",
            status="Running",
            programs=self.get_programs(),
            cpu_load=round(random.uniform(12.0, 28.0), 1),
            memory_used=49152,     # 48 KB of 64 KB used
            memory_total=65536,
        )
