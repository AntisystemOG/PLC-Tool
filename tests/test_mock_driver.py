import pytest

from plc_tools.communication.mock_driver import MockDriver
from plc_tools.communication.models import PLCType


@pytest.fixture
def driver():
    d = MockDriver()
    d.connect()
    return d


def test_connect(driver):
    assert driver.is_connected


def test_disconnect(driver):
    driver.disconnect()
    assert not driver.is_connected


def test_read_known_tag(driver):
    tag = driver.read_tag("Global_SystemReady")
    assert tag.is_valid
    assert tag.data_type == "BOOL"


def test_read_unknown_tag(driver):
    tag = driver.read_tag("DoesNotExist")
    assert not tag.is_valid
    assert tag.error is not None


def test_read_multiple_tags(driver):
    tags = driver.read_tags(["Global_SystemReady", "Global_CycleCount"])
    assert len(tags) == 2
    assert all(t.is_valid for t in tags)


def test_write_tag(driver):
    ok = driver.write_tag("Global_SystemReady", False)
    assert ok
    tag = driver.read_tag("Global_SystemReady")
    assert tag.value is False


def test_write_unknown_tag(driver):
    ok = driver.write_tag("NonExistent", 42)
    assert not ok


def test_get_tag_list(driver):
    tags = driver.get_tag_list()
    assert len(tags) > 0
    names = [t.name for t in tags]
    assert "Global_SystemReady" in names


def test_get_programs(driver):
    programs = driver.get_programs()
    assert len(programs) > 0
    names = [p.name for p in programs]
    assert "MainProgram" in names


def test_get_io_modules(driver):
    modules = driver.get_io_modules()
    assert len(modules) > 0
    slots = [m.slot for m in modules]
    assert 0 in slots


def test_get_fault_log(driver):
    faults = driver.get_fault_log()
    assert len(faults) > 0


def test_get_controller_info(driver):
    info = driver.get_controller_info()
    assert info.name == "Mock_Controller"
    assert info.cpu_load > 0
    assert info.memory_total > 0


def test_context_manager():
    with MockDriver() as d:
        assert d.is_connected
    assert not d.is_connected
