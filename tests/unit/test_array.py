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

import packtype
from packtype import Constant, Packing, Scalar

from ..fixtures import reset_registry

assert reset_registry


def test_array():
    @packtype.package()
    class TestPkg:
        EF_NUM: Constant = 2

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: 3 * Scalar[3]
        ef: TestPkg.EF_NUM * Scalar[9]

    inst = TestStruct()
    assert inst._pt_width == 12 + (3 * 3) + (2 * 9)
    assert inst.ab._pt_width == 12
    assert inst.cd[0]._pt_width == 3
    assert inst.cd[1]._pt_width == 3
    assert inst.cd[2]._pt_width == 3
    assert inst.ef[0]._pt_width == 9
    assert inst.ef[1]._pt_width == 9


def test_array_pack():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: 3 * Scalar[3]
        ef: Scalar[9]

    inst = TestStruct()
    inst.ab = 123
    inst.cd[0] = 1
    inst.cd[1] = 2
    inst.cd[2] = 3
    inst.ef = 53
    assert inst._pt_pack() == ((53 << 21) | (3 << 18) | (2 << 15) | (1 << 12) | 123)
    assert int(inst) == ((53 << 21) | (3 << 18) | (2 << 15) | (1 << 12) | 123)


def test_array_pack_from_msb():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(packing=Packing.FROM_MSB)
    class TestStruct:
        ab: Scalar[12]
        cd: 3 * Scalar[3]
        ef: Scalar[9]

    inst = TestStruct()
    inst.ab = 123
    inst.cd[0] = 1
    inst.cd[1] = 2
    inst.cd[2] = 3
    inst.ef = 53
    assert inst._pt_pack() == ((123 << 18) | (1 << 15) | (2 << 12) | (3 << 9) | 53)
    assert int(inst) == ((123 << 18) | (1 << 15) | (2 << 12) | (3 << 9) | 53)


def test_array_unpack():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: 3 * Scalar[3]
        ef: Scalar[9]

    inst = TestStruct._pt_unpack((53 << 21) | (3 << 18) | (2 << 15) | (1 << 12) | 123)
    assert int(inst.ab) == 123
    assert int(inst.cd[0]) == 1
    assert int(inst.cd[1]) == 2
    assert int(inst.cd[2]) == 3
    assert int(inst.ef) == 53


def test_array_unpack_from_msb():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(packing=Packing.FROM_MSB)
    class TestStruct:
        ab: Scalar[12]
        cd: 3 * Scalar[3]
        ef: Scalar[9]

    inst = TestStruct._pt_unpack((123 << 18) | (1 << 15) | (2 << 12) | (3 << 9) | 53)
    assert int(inst.ab) == 123
    assert int(inst.cd[0]) == 1
    assert int(inst.cd[1]) == 2
    assert int(inst.cd[2]) == 3
    assert int(inst.ef) == 53
