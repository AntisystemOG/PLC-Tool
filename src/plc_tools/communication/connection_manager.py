from __future__ import annotations

from .base_driver import BasePLCDriver
from .logix_driver import LogixDriver
from .micro800_driver import Micro800Driver
from .mock_driver import MockDriver
from .models import ConnectionConfig, PLCType


class ConnectionManager:
    def __init__(self) -> None:
        self._driver: BasePLCDriver | None = None
        self._config: ConnectionConfig | None = None

    @property
    def driver(self) -> BasePLCDriver | None:
        return self._driver

    @property
    def is_connected(self) -> bool:
        return self._driver is not None and self._driver.is_connected

    @property
    def config(self) -> ConnectionConfig | None:
        return self._config

    def connect(self, config: ConnectionConfig) -> bool:
        self.disconnect()
        driver = self._create_driver(config)
        success = driver.connect()
        if success:
            self._driver = driver
            self._config = config
        return success

    def disconnect(self) -> None:
        if self._driver is not None:
            self._driver.disconnect()
            self._driver = None
            self._config = None

    def _create_driver(self, config: ConnectionConfig) -> BasePLCDriver:
        if config.plc_type == PLCType.LOGIX:
            return LogixDriver(config)
        if config.plc_type == PLCType.MICRO800:
            return Micro800Driver(config)
        if config.plc_type == PLCType.MOCK:
            return MockDriver(config)
        raise ValueError(f"Unknown PLC type: {config.plc_type}")

    def __repr__(self) -> str:
        if self._config:
            status = "connected" if self.is_connected else "disconnected"
            return f"ConnectionManager({self._config.ip_address}, {status})"
        return "ConnectionManager(disconnected)"
