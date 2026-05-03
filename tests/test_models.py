from datetime import datetime

import pytest

from plc_tools.communication.models import (
    ConnectionConfig,
    ControllerInfo,
    FaultEntry,
    FaultType,
    IOChannel,
    IOModule,
    PLCType,
    TagValue,
)


def test_connection_config_default_name():
    cfg = ConnectionConfig(ip_address="10.0.0.1")
    assert cfg.name == "10.0.0.1"


def test_connection_config_explicit_name():
    cfg = ConnectionConfig(ip_address="10.0.0.1", name="MyPLC")
    assert cfg.name == "MyPLC"


def test_tag_value_valid():
    tag = TagValue(name="Motor_Run", value=True, data_type="BOOL")
    assert tag.is_valid
    assert "Motor_Run" in str(tag)


def test_tag_value_error():
    tag = TagValue(name="Bad_Tag", value=None, data_type="UNKNOWN", error="Not found")
    assert not tag.is_valid
    assert "ERROR" in str(tag)


def test_io_module_faulted():
    mod = IOModule(slot=1, name="DI", vendor="AB", catalog="1756-IB16", status="Faulted")
    assert mod.is_faulted


def test_io_module_ok():
    mod = IOModule(slot=1, name="DI", vendor="AB", catalog="1756-IB16", status="Running")
    assert not mod.is_faulted


def test_fault_entry_str():
    fault = FaultEntry(
        code=0x0042,
        description="Watchdog timeout",
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        fault_type=FaultType.MAJOR,
    )
    s = str(fault)
    assert "MAJOR" in s
    assert "0042" in s


def test_controller_info_memory_percent():
    info = ControllerInfo(
        name="Test",
        serial_number="",
        firmware="",
        catalog="",
        vendor="",
        keyswitch="",
        status="",
        memory_used=512,
        memory_total=1024,
    )
    assert info.memory_percent == 50.0


def test_controller_info_zero_memory():
    info = ControllerInfo(
        name="Test", serial_number="", firmware="", catalog="", vendor="", keyswitch="", status=""
    )
    assert info.memory_percent == 0.0
