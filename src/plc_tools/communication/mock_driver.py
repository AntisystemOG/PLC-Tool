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

_MOCK_TAGS: dict[str, tuple[Any, str]] = {
    "Program:MainProgram.Motor1_Run": (False, "BOOL"),
    "Program:MainProgram.Motor1_Speed": (1750.0, "REAL"),
    "Program:MainProgram.Motor1_Fault": (False, "BOOL"),
    "Program:MainProgram.Tank1_Level": (75.3, "REAL"),
    "Program:MainProgram.Tank1_High": (False, "BOOL"),
    "Program:MainProgram.Tank1_Low": (False, "BOOL"),
    "Program:MainProgram.Conveyor_Run": (True, "BOOL"),
    "Program:MainProgram.Conveyor_Speed": (60.0, "REAL"),
    "Program:MainProgram.Conveyor_Fault": (False, "BOOL"),
    "Program:SafetyProgram.EStop_OK": (True, "BOOL"),
    "Program:SafetyProgram.GuardDoor_Closed": (True, "BOOL"),
    "Global_HeartBeat": (0, "DINT"),
    "Global_SystemReady": (True, "BOOL"),
    "Global_AlarmCount": (0, "DINT"),
    "Global_CycleCount": (12483, "DINT"),
}


class MockDriver(BasePLCDriver):
    def __init__(self, config: ConnectionConfig | None = None) -> None:
        if config is None:
            config = ConnectionConfig(ip_address="192.168.1.1", plc_type=PLCType.MOCK, name="Mock PLC")
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
            value = value + random.uniform(-0.5, 0.5)
        elif tag_name == "Global_HeartBeat":
            value = self._cycle % 32767
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
                name="MainProgram",
                program_type="Normal",
                routines=[
                    RoutineInfo("MainRoutine", "LAD"),
                    RoutineInfo("MotorControl", "LAD"),
                    RoutineInfo("TankControl", "LAD"),
                    RoutineInfo("ConveyorControl", "LAD"),
                    RoutineInfo("AlarmRoutine", "LAD"),
                ],
            ),
            ProgramInfo(
                name="SafetyProgram",
                program_type="Safety",
                routines=[
                    RoutineInfo("SafetyMain", "LAD"),
                    RoutineInfo("EStopLogic", "LAD"),
                ],
            ),
        ]

    def get_io_modules(self) -> list[IOModule]:
        return [
            IOModule(
                slot=0,
                name="ControlLogix Controller",
                vendor="Allen-Bradley",
                catalog="1756-L85E",
                status="Running",
                channels=[],
            ),
            IOModule(
                slot=1,
                name="Digital Input Module",
                vendor="Allen-Bradley",
                catalog="1756-IB16",
                status="Running",
                channels=[
                    IOChannel(i, f"DI:{i:02d}", bool(random.randint(0, 1)), True)
                    for i in range(16)
                ],
            ),
            IOModule(
                slot=2,
                name="Digital Output Module",
                vendor="Allen-Bradley",
                catalog="1756-OB16",
                status="Running",
                channels=[
                    IOChannel(i, f"DO:{i:02d}", bool(random.randint(0, 1)), False)
                    for i in range(16)
                ],
            ),
            IOModule(
                slot=3,
                name="Analog Input Module",
                vendor="Allen-Bradley",
                catalog="1756-IF8",
                status="Running",
                channels=[
                    IOChannel(i, f"AI:{i:02d}", round(random.uniform(0.0, 10.0), 3), True)
                    for i in range(8)
                ],
            ),
        ]

    def get_fault_log(self) -> list[FaultEntry]:
        now = datetime.now()
        return [
            FaultEntry(
                code=0x0001,
                description="Minor fault: I/O module in slot 3 configuration mismatch",
                timestamp=now - timedelta(hours=2, minutes=15),
                fault_type=FaultType.MINOR,
                program="",
            ),
            FaultEntry(
                code=0x0042,
                description="Major fault: Task watchdog timeout in MainProgram",
                timestamp=now - timedelta(days=1, hours=4),
                fault_type=FaultType.MAJOR,
                program="MainProgram",
            ),
            FaultEntry(
                code=0x0010,
                description="I/O fault: Communication loss on slot 2",
                timestamp=now - timedelta(days=3),
                fault_type=FaultType.IO,
                program="",
            ),
        ]

    def get_controller_info(self) -> ControllerInfo:
        return ControllerInfo(
            name="Mock_Controller",
            serial_number="00FF1234",
            firmware="35.011",
            catalog="1756-L85E",
            vendor="Allen-Bradley",
            keyswitch="Run",
            status="Running",
            programs=self.get_programs(),
            cpu_load=round(random.uniform(10.0, 35.0), 1),
            memory_used=524288,
            memory_total=2097152,
        )
