# Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk
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

import pytest

from packtype.__main__ import main

def test_integ_constant(tmpdir):
    """ Generate a basic package with constants  """
    # Create a specification
    with open(tmpdir / "spec.py", "w") as fh:
        fh.write("\n".join([
            "import packtype",
            "from packtype import Constant",
            "@packtype.package()",
            "class TestPackage:",
            "    CONST_A : Constant('hello'   ) = 0x1234",
            "    CONST_B : Constant('goodbye' ) = 0x5678",
            "    CONST_C : Constant('farewell') = 0x9ABC",
        ]))
    # Invoke packtype's CLI
    with pytest.raises(SystemExit):
        main.main([
            str(tmpdir / "spec.py"),
            str(tmpdir),
            "--render", "c",
        ])
    # Read in the header file and strip blank lines
    with open(tmpdir / "test_package.h", "r") as fh:
        lines = list(filter(
            lambda x: len(x.strip()) > 0 and not x.startswith("//"),
            fh.readlines()
        ))
        assert lines == [
            "#ifndef __TEST_PACKAGE_H__\n",
            "#define __TEST_PACKAGE_H__\n",
            "#include <stdint.h>\n",
            "#include <string.h>\n",
            "const uint32_t TEST_PACKAGE_CONST_A = 0x00001234;\n",
            "const uint32_t TEST_PACKAGE_CONST_B = 0x00005678;\n",
            "const uint32_t TEST_PACKAGE_CONST_C = 0x00009ABC;\n",
            "#endif // __TEST_PACKAGE_H__\n",
        ]
