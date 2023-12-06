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

def test_union():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.union()
    class TestUnion:
        a: Scalar[13]
        b: Scalar[13]
        c: Scalar[13]

    inst = TestUnion()
    inst.a = 123
    assert int(inst.a) == 123
    assert int(inst.b) == 123
    assert int(inst.c) == 123
    inst.c = 62
    assert int(inst.a) == 62
    assert int(inst.b) == 62
    assert int(inst.c) == 62
