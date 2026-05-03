from __future__ import annotations

import csv
from pathlib import Path

from plc_tools.communication.models import FaultEntry, TagValue

try:
    from texttable import Texttable

    _TEXTTABLE = True
except ImportError:
    _TEXTTABLE = False


class ReportGenerator:
    def export_fault_log(self, faults: list[FaultEntry], path: str) -> None:
        p = Path(path)
        if p.suffix.lower() == ".csv":
            self._faults_csv(faults, path)
        else:
            self._faults_text(faults, path)

    def export_tag_list(self, tags: list[TagValue], path: str) -> None:
        p = Path(path)
        if p.suffix.lower() == ".csv":
            self._tags_csv(tags, path)
        else:
            self._tags_text(tags, path)

    def _faults_csv(self, faults: list[FaultEntry], path: str) -> None:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Type", "Code", "Program", "Description"])
            for fault in faults:
                writer.writerow([
                    fault.timestamp.isoformat(),
                    fault.fault_type.value,
                    f"0x{fault.code:04X}",
                    fault.program,
                    fault.description,
                ])

    def _faults_text(self, faults: list[FaultEntry], path: str) -> None:
        with open(path, "w") as f:
            if _TEXTTABLE:
                t = Texttable(max_width=120)
                t.header(["Timestamp", "Type", "Code", "Program", "Description"])
                for fault in faults:
                    t.add_row([
                        fault.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        fault.fault_type.value.upper(),
                        f"0x{fault.code:04X}",
                        fault.program,
                        fault.description,
                    ])
                f.write(t.draw())
            else:
                for fault in faults:
                    f.write(str(fault) + "\n")

    def _tags_csv(self, tags: list[TagValue], path: str) -> None:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Tag Name", "Data Type"])
            for tag in tags:
                writer.writerow([tag.name, tag.data_type])

    def _tags_text(self, tags: list[TagValue], path: str) -> None:
        with open(path, "w") as f:
            if _TEXTTABLE:
                t = Texttable(max_width=100)
                t.header(["Tag Name", "Data Type"])
                for tag in tags:
                    t.add_row([tag.name, tag.data_type])
                f.write(t.draw())
            else:
                for tag in tags:
                    f.write(f"{tag.name}\t{tag.data_type}\n")
