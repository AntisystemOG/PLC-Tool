from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import ConnectionConfig, ControllerInfo, FaultEntry, IOModule, ProgramInfo, TagValue


class BasePLCDriver(ABC):
    def __init__(self, config: ConnectionConfig) -> None:
        self.config = config
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def read_tag(self, tag_name: str) -> TagValue: ...

    @abstractmethod
    def read_tags(self, tag_names: list[str]) -> list[TagValue]: ...

    @abstractmethod
    def write_tag(self, tag_name: str, value: Any) -> bool: ...

    @abstractmethod
    def get_tag_list(self) -> list[TagValue]: ...

    @abstractmethod
    def get_programs(self) -> list[ProgramInfo]: ...

    @abstractmethod
    def get_io_modules(self) -> list[IOModule]: ...

    @abstractmethod
    def get_fault_log(self) -> list[FaultEntry]: ...

    @abstractmethod
    def get_controller_info(self) -> ControllerInfo: ...

    def __enter__(self) -> "BasePLCDriver":
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()

    def __repr__(self) -> str:
        status = "connected" if self._connected else "disconnected"
        return f"{self.__class__.__name__}({self.config.ip_address}, {status})"
