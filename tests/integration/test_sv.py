# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import subprocess
from pathlib import Path

resources = Path(__file__).parent.absolute() / "resources"


def test_sv(tmp_path):
    # Wrap around the CLI
    result = subprocess.run(
        (
            "python3",
            "-m",
            "packtype",
            "--debug",
            (resources / "test_pkg.py").as_posix(),
            "code",
            "package",
            "sv",
            tmp_path.as_posix(),
        ),
        check=True,
        cwd=Path(__file__).parent.parent.parent.absolute(),
    )
    assert result.returncode == 0
    assert (tmp_path / "other_pkg.sv").exists()
    assert (tmp_path / "test_pkg.sv").exists()


def test_sv_only(tmp_path):
    # Wrap around the CLI
    result = subprocess.run(
        (
            "python3",
            "-m",
            "packtype",
            "--debug",
            (resources / "test_pkg.py").as_posix(),
            "code",
            "package",
            "sv",
            tmp_path.as_posix(),
            "TestPkg",
        ),
        check=True,
        cwd=Path(__file__).parent.parent.parent.absolute(),
    )
    assert result.returncode == 0
    assert not (tmp_path / "other_pkg.sv").exists()
    assert (tmp_path / "test_pkg.sv").exists()
