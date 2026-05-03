import textwrap
from pathlib import Path

import pytest

from plc_tools.communication.l5x_parser import parse_l5x


SAMPLE_L5X = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <RSLogix5000Content>
      <Controller Name="TestController" ProcessorType="1756-L85E" MajorRev="35" MinorRev="11">
        <Tags>
          <Tag Name="GlobalTag1" DataType="BOOL" Radix="Decimal"/>
          <Tag Name="GlobalTag2" DataType="DINT" Radix="Decimal"/>
        </Tags>
        <Programs>
          <Program Name="MainProgram" Type="Normal">
            <Tags>
              <Tag Name="LocalTag1" DataType="REAL" Radix="Float"/>
            </Tags>
            <Routines>
              <Routine Name="MainRoutine" Type="RLL">
                <RLLContent>
                  <Rung Number="0" Type="N"/>
                  <Rung Number="1" Type="N"/>
                </RLLContent>
              </Routine>
              <Routine Name="MotorControl" Type="RLL"/>
            </Routines>
          </Program>
        </Programs>
        <DataTypes/>
      </Controller>
    </RSLogix5000Content>
""")


@pytest.fixture
def l5x_file(tmp_path: Path) -> Path:
    p = tmp_path / "test.L5X"
    p.write_text(SAMPLE_L5X)
    return p


def test_parse_controller_name(l5x_file):
    project = parse_l5x(l5x_file)
    assert project.controller_name == "TestController"


def test_parse_processor_type(l5x_file):
    project = parse_l5x(l5x_file)
    assert project.processor_type == "1756-L85E"


def test_parse_revision(l5x_file):
    project = parse_l5x(l5x_file)
    assert project.major_revision == "35"
    assert project.minor_revision == "11"


def test_parse_controller_tags(l5x_file):
    project = parse_l5x(l5x_file)
    assert len(project.controller_tags) == 2
    names = [t.name for t in project.controller_tags]
    assert "GlobalTag1" in names
    assert "GlobalTag2" in names


def test_parse_programs(l5x_file):
    project = parse_l5x(l5x_file)
    assert len(project.programs) == 1
    assert project.programs[0].name == "MainProgram"


def test_parse_routines(l5x_file):
    project = parse_l5x(l5x_file)
    routines = project.programs[0].routines
    assert len(routines) == 2
    names = [r.name for r in routines]
    assert "MainRoutine" in names
    assert "MotorControl" in names


def test_parse_rung_count(l5x_file):
    project = parse_l5x(l5x_file)
    main_routine = next(r for r in project.programs[0].routines if r.name == "MainRoutine")
    assert main_routine.rung_count == 2


def test_parse_program_tags(l5x_file):
    project = parse_l5x(l5x_file)
    prog_tags = project.programs[0].tags
    assert len(prog_tags) == 1
    assert prog_tags[0].name == "LocalTag1"
    assert prog_tags[0].scope == "MainProgram"


def test_invalid_file(tmp_path):
    bad = tmp_path / "bad.L5X"
    bad.write_text("<RSLogix5000Content><NotAController/></RSLogix5000Content>")
    with pytest.raises(ValueError, match="No Controller element"):
        parse_l5x(bad)
