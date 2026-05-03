from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .models import ConnectionConfig, PLCType


@dataclass
class ProjectEntry:
    name: str
    ip_address: str
    slot: int
    plc_type: str
    notes: str = ""

    def to_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            ip_address=self.ip_address,
            slot=self.slot,
            plc_type=PLCType(self.plc_type),
            name=self.name,
        )


class ProjectManager:
    _DEFAULT_PATH = Path.home() / ".plc_tools" / "projects.json"

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or self._DEFAULT_PATH
        self._entries: list[ProjectEntry] = []
        self._load()

    @property
    def entries(self) -> list[ProjectEntry]:
        return list(self._entries)

    def add(self, entry: ProjectEntry) -> None:
        self._entries = [e for e in self._entries if e.name != entry.name]
        self._entries.append(entry)
        self._save()

    def remove(self, name: str) -> None:
        self._entries = [e for e in self._entries if e.name != name]
        self._save()

    def get(self, name: str) -> ProjectEntry | None:
        return next((e for e in self._entries if e.name == name), None)

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            with self._path.open() as f:
                data = json.load(f)
            self._entries = [ProjectEntry(**item) for item in data]
        except Exception:
            self._entries = []

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w") as f:
            json.dump([asdict(e) for e in self._entries], f, indent=2)
