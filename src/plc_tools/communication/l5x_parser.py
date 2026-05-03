from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class L5XTag:
    name: str
    data_type: str
    scope: str
    description: str = ""
    dimensions: str = ""
    radix: str = ""
    value: Any = None


@dataclass
class L5XRoutine:
    name: str
    routine_type: str
    description: str = ""
    rung_count: int = 0


@dataclass
class L5XProgram:
    name: str
    description: str = ""
    tags: list[L5XTag] = field(default_factory=list)
    routines: list[L5XRoutine] = field(default_factory=list)


@dataclass
class L5XProject:
    controller_name: str
    processor_type: str
    major_revision: str
    minor_revision: str
    programs: list[L5XProgram] = field(default_factory=list)
    controller_tags: list[L5XTag] = field(default_factory=list)
    data_types: list[str] = field(default_factory=list)


def _parse_tag(elem: ET.Element, scope: str) -> L5XTag:
    return L5XTag(
        name=elem.get("Name", ""),
        data_type=elem.get("DataType", ""),
        scope=scope,
        description=elem.findtext("Description", ""),
        dimensions=elem.get("Dimensions", ""),
        radix=elem.get("Radix", ""),
    )


def _parse_routine(elem: ET.Element) -> L5XRoutine:
    rung_count = len(elem.findall(".//Rung"))
    return L5XRoutine(
        name=elem.get("Name", ""),
        routine_type=elem.get("Type", "LAD"),
        description=elem.findtext("Description", ""),
        rung_count=rung_count,
    )


def _parse_program(elem: ET.Element) -> L5XProgram:
    name = elem.get("Name", "")
    prog = L5XProgram(
        name=name,
        description=elem.findtext("Description", ""),
    )
    tags_elem = elem.find("Tags")
    if tags_elem is not None:
        for tag_elem in tags_elem.findall("Tag"):
            prog.tags.append(_parse_tag(tag_elem, name))
    routines_elem = elem.find("Routines")
    if routines_elem is not None:
        for routine_elem in routines_elem.findall("Routine"):
            prog.routines.append(_parse_routine(routine_elem))
    return prog


def parse_l5x(path: str | Path) -> L5XProject:
    tree = ET.parse(str(path))
    root = tree.getroot()
    controller = root.find("Controller")
    if controller is None:
        raise ValueError("No Controller element found in L5X file")

    project = L5XProject(
        controller_name=controller.get("Name", ""),
        processor_type=controller.get("ProcessorType", ""),
        major_revision=controller.get("MajorRev", ""),
        minor_revision=controller.get("MinorRev", ""),
    )

    tags_elem = controller.find("Tags")
    if tags_elem is not None:
        for tag_elem in tags_elem.findall("Tag"):
            project.controller_tags.append(_parse_tag(tag_elem, "Controller"))

    programs_elem = controller.find("Programs")
    if programs_elem is not None:
        for prog_elem in programs_elem.findall("Program"):
            project.programs.append(_parse_program(prog_elem))

    dt_elem = controller.find("DataTypes")
    if dt_elem is not None:
        project.data_types = [e.get("Name", "") for e in dt_elem.findall("DataType")]

    return project
