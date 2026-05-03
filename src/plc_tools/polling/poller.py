from __future__ import annotations

import threading
from typing import Callable

from plc_tools.communication.connection_manager import ConnectionManager
from plc_tools.communication.models import TagValue


class Poller:
    def __init__(self, connection_manager: ConnectionManager) -> None:
        self._manager = connection_manager
        self._tags: list[str] = []
        self._lock = threading.Lock()
        self._callbacks: list[Callable[[list[TagValue]], None]] = []

    def add_tag(self, name: str) -> None:
        with self._lock:
            if name not in self._tags:
                self._tags.append(name)

    def remove_tag(self, name: str) -> None:
        with self._lock:
            if name in self._tags:
                self._tags.remove(name)

    def clear(self) -> None:
        with self._lock:
            self._tags.clear()

    def add_callback(self, cb: Callable[[list[TagValue]], None]) -> None:
        self._callbacks.append(cb)

    def poll(self) -> list[TagValue]:
        with self._lock:
            tags = list(self._tags)
        if not tags or not self._manager.is_connected:
            return []
        values = self._manager.driver.read_tags(tags)
        for cb in self._callbacks:
            cb(values)
        return values

    @property
    def watched_tags(self) -> list[str]:
        with self._lock:
            return list(self._tags)
