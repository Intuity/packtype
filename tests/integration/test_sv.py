# Copyright 2024, Peter Birch, mailto:peter@intuity.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
