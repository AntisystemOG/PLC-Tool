import json
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from plc_tools.communication.models import TagValue
from plc_tools.recording.recorder import MAX_DURATION_SECONDS, DataRecorder


@pytest.fixture
def recorder():
    return DataRecorder()


@pytest.fixture
def tmp_json(tmp_path):
    return str(tmp_path / "recording.json")


def _make_tags(values: dict) -> list[TagValue]:
    return [TagValue(name=k, value=v, data_type="REAL") for k, v in values.items()]


def test_initial_state(recorder):
    assert not recorder.is_active
    assert recorder.sample_count == 0
    assert recorder.elapsed_seconds == 0.0


def test_start_creates_file(recorder, tmp_json):
    recorder.start(tmp_json)
    assert recorder.is_active
    assert Path(tmp_json).exists()
    recorder.stop()


def test_stop_writes_valid_json(recorder, tmp_json):
    recorder.start(tmp_json)
    recorder.record(_make_tags({"Motor_Speed": 1750.0, "Motor_Run": True}))
    recorder.record(_make_tags({"Motor_Speed": 1752.3, "Motor_Run": True}))
    recorder.stop()

    data = json.loads(Path(tmp_json).read_text())
    assert isinstance(data, list)
    assert len(data) == 2


def test_record_structure(recorder, tmp_json):
    recorder.start(tmp_json)
    recorder.record(_make_tags({"Tag1": 42.0, "Tag2": True}))
    recorder.stop()

    entry = json.loads(Path(tmp_json).read_text())[0]
    assert "timestamp" in entry
    assert "elapsed_seconds" in entry
    assert "tags" in entry
    assert entry["tags"]["Tag1"] == 42.0
    assert entry["tags"]["Tag2"] is True


def test_invalid_tags_excluded(recorder, tmp_json):
    tags = [
        TagValue(name="Good", value=1.0, data_type="REAL"),
        TagValue(name="Bad", value=None, data_type="UNKNOWN", error="timeout"),
    ]
    recorder.start(tmp_json)
    recorder.record(tags)
    recorder.stop()

    entry = json.loads(Path(tmp_json).read_text())[0]
    assert "Good" in entry["tags"]
    assert "Bad" not in entry["tags"]


def test_sample_count(recorder, tmp_json):
    recorder.start(tmp_json)
    for _ in range(5):
        recorder.record(_make_tags({"T": 1.0}))
    recorder.stop()
    assert recorder.sample_count == 5


def test_record_after_stop_is_noop(recorder, tmp_json):
    recorder.start(tmp_json)
    recorder.stop()
    recorder.record(_make_tags({"T": 1.0}))
    assert recorder.sample_count == 0


def test_auto_stop_triggers_callback(recorder, tmp_json):
    called = []
    recorder.on_auto_stopped = lambda: called.append(True)

    with patch("plc_tools.recording.recorder.MAX_DURATION_SECONDS", 0):
        recorder.start(tmp_json)
        recorder.record(_make_tags({"T": 1.0}))

    assert called == [True]
    assert not recorder.is_active


def test_elapsed_and_remaining(recorder, tmp_json):
    recorder.start(tmp_json)
    assert recorder.elapsed_seconds >= 0.0
    assert recorder.remaining_seconds <= MAX_DURATION_SECONDS
    recorder.stop()


def test_empty_tag_list(recorder, tmp_json):
    recorder.start(tmp_json)
    recorder.record([])
    recorder.stop()
    data = json.loads(Path(tmp_json).read_text())
    assert len(data) == 1
    assert data[0]["tags"] == {}
