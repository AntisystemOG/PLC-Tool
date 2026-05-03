from __future__ import annotations

import json
from datetime import datetime
from typing import Callable

from plc_tools.communication.models import TagValue

MAX_DURATION_SECONDS = 12 * 3600


class DataRecorder:
    def __init__(self) -> None:
        self._file = None
        self._path: str = ""
        self._start_time: datetime | None = None
        self._sample_count: int = 0
        self._first_record: bool = True
        self._active: bool = False
        self.on_auto_stopped: Callable[[], None] | None = None

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def path(self) -> str:
        return self._path

    @property
    def elapsed_seconds(self) -> float:
        if self._start_time is None:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, MAX_DURATION_SECONDS - self.elapsed_seconds)

    @property
    def sample_count(self) -> int:
        return self._sample_count

    def start(self, path: str) -> None:
        self._path = path
        self._file = open(path, "w")
        self._file.write("[\n")
        self._start_time = datetime.now()
        self._sample_count = 0
        self._first_record = True
        self._active = True

    def record(self, tag_values: list[TagValue]) -> None:
        if not self._active or self._file is None:
            return

        if self.elapsed_seconds >= MAX_DURATION_SECONDS:
            self.stop()
            if self.on_auto_stopped:
                self.on_auto_stopped()
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "tags": {tv.name: tv.value for tv in tag_values if tv.is_valid},
        }

        if not self._first_record:
            self._file.write(",\n")
        self._first_record = False

        json.dump(entry, self._file)
        self._file.flush()
        self._sample_count += 1

    def stop(self) -> None:
        if self._file is not None:
            self._file.write("\n]\n")
            self._file.close()
            self._file = None
        self._active = False
