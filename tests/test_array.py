# Copyright 2023, Peter Birch, mailto:peter@intuity.io
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
import packtype
from packtype import Packing, Scalar
from packtype.assembly import WidthError

def test_array():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: 3 * Scalar[3]
        ef: Scalar[9]

    inst = TestStruct()
    assert inst._pt_width == 12 + (3 * 3) + 9
    assert inst.ab._pt_width == 12
    assert inst.cd[0]._pt_width == 3
    assert inst.cd[1]._pt_width == 3
    assert inst.cd[2]._pt_width == 3
    assert inst.ef._pt_width == 9
