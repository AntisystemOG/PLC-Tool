from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PLCType(Enum):
    LOGIX = "logix"
    MICRO800 = "micro800"
    MOCK = "mock"


class FaultType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    IO = "io"


@dataclass
class ConnectionConfig:
    ip_address: str
    slot: int = 0
    plc_type: PLCType = PLCType.LOGIX
    name: str = ""
    timeout: float = 5.0

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.ip_address


@dataclass
class TagValue:
    name: str
    value: Any
    data_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    error: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.error is None

    def __str__(self) -> str:
        if self.error:
            return f"{self.name}: ERROR({self.error})"
        return f"{self.name}: {self.value} ({self.data_type})"


@dataclass
class IOChannel:
    channel: int
    name: str
    value: bool | int | float
    is_input: bool


@dataclass
class IOModule:
    slot: int
    name: str
    vendor: str
    catalog: str
    status: str
    channels: list[IOChannel] = field(default_factory=list)

    @property
    def is_faulted(self) -> bool:
        return "fault" in self.status.lower()


@dataclass
class FaultEntry:
    code: int
    description: str
    timestamp: datetime
    fault_type: FaultType
    program: str = ""

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{ts}] {self.fault_type.value.upper()} Fault {self.code:04X}: {self.description}"


@dataclass
class RoutineInfo:
    name: str
    routine_type: str


@dataclass
class ProgramInfo:
    name: str
    program_type: str
    routines: list[RoutineInfo] = field(default_factory=list)


@dataclass
class ControllerInfo:
    name: str
    serial_number: str
    firmware: str
    catalog: str
    vendor: str
    keyswitch: str
    status: str
    programs: list[ProgramInfo] = field(default_factory=list)
    cpu_load: float = 0.0
    memory_used: int = 0
    memory_total: int = 0

    @property
    def memory_percent(self) -> float:
        if self.memory_total == 0:
            return 0.0
        return (self.memory_used / self.memory_total) * 100
