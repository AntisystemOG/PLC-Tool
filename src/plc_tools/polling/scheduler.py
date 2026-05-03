from __future__ import annotations

import threading
from typing import Callable


class Scheduler:
    def __init__(self) -> None:
        self._tasks: dict[str, tuple[float, Callable[[], None]]] = {}
        self._lock = threading.Lock()

    def add(self, name: str, interval_ms: float, callback: Callable[[], None]) -> None:
        with self._lock:
            self._tasks[name] = (interval_ms, callback)

    def remove(self, name: str) -> None:
        with self._lock:
            self._tasks.pop(name, None)

    def get_interval(self, name: str) -> float | None:
        with self._lock:
            entry = self._tasks.get(name)
            return entry[0] if entry else None

    def set_interval(self, name: str, interval_ms: float) -> None:
        with self._lock:
            if name in self._tasks:
                _, cb = self._tasks[name]
                self._tasks[name] = (interval_ms, cb)

    @property
    def task_names(self) -> list[str]:
        with self._lock:
            return list(self._tasks.keys())
