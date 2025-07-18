# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import subprocess
from pathlib import Path

import packtype
from packtype import Scalar
from packtype.svg.render import SvgConfig

from ..fixtures import reset_registry

assert reset_registry


REFERENCE = Path(__file__).parent / "reference"


def test_struct_svg_single():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        abc: Scalar[32]

    inst = TestStruct()
    svg = inst._repr_svg_()
    assert svg.strip() == (REFERENCE / "test_struct_svg_single.svg").read_text("utf-8").strip()


def test_struct_svg_multiple():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        a: Scalar[8]
        b: Scalar[8]
        e: Scalar[32]
        c: Scalar[8]
        d: Scalar[8]

    inst = TestStruct()
    svg = inst._repr_svg_()
    assert svg.strip() == (REFERENCE / "test_struct_svg_multiple.svg").read_text("utf-8").strip()


def test_struct_svg_nested():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class InnerStruct:
        a: Scalar[8]
        b: Scalar[8]

    @TestPkg.struct()
    class OuterStruct:
        c: Scalar[8]
        inner: InnerStruct
        d: Scalar[8]

    inst = OuterStruct()
    svg = inst._repr_svg_()
    assert svg.strip() == (REFERENCE / "test_struct_svg_nested.svg").read_text("utf-8").strip()


def test_struct_svg_custom_style():
    cfg = SvgConfig()
    cfg.per_bit_width = 40
    cfg.cell_height = 30
    cfg.box_style.stroke = "red"
    cfg.hatching.stroke = "blue"

    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(width=32)
    class TestStruct:
        abc: Scalar[16]

    inst = TestStruct()
    svg = inst._pt_as_svg(cfg)
    assert (
        svg.strip() == (REFERENCE / "test_struct_svg_custom_style.svg").read_text("utf-8").strip()
    )


def test_struct_svg_command(tmp_path):
    # Wrap around the CLI
    result = subprocess.run(
        (
            "python3",
            "-m",
            "packtype",
            "svg",
            "DemoPkg.TestStruct",
            (REFERENCE / "demo_pkg.py").as_posix(),
        ),
        cwd=Path(__file__).parent.parent.parent.absolute(),
        capture_output=True,
        check=True,
    )
    assert result.returncode == 0
    assert (
        result.stdout.decode("utf-8").strip()
        == (REFERENCE / "test_struct_svg_command.svg").read_text("utf-8").strip()
    )
