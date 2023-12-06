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


def test_struct():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    inst = TestStruct()
    assert inst._pt_width == 12 + 3 + 9
    assert inst.ab._pt_width == 12
    assert inst.cd._pt_width == 3
    assert inst.ef._pt_width == 9


def test_struct_packing():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    inst = TestStruct()
    inst.ab = 123
    inst.cd = 5
    inst.ef = 39

    assert inst.ab.value == 123
    assert inst.cd.value == 5
    assert inst.ef.value == 39
    assert inst._pt_pack() == (39 << 15) | (5 << 12) | 123
    assert int(inst) == (39 << 15) | (5 << 12) | 123


def test_struct_packing_from_msb():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(packing=Packing.FROM_MSB)
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    inst = TestStruct()
    inst.ab = 123
    inst.cd = 5
    inst.ef = 39

    assert inst.ab.value == 123
    assert inst.cd.value == 5
    assert inst.ef.value == 39
    assert inst._pt_pack() == (123 << 12) | (5 << 9) | 39
    assert int(inst) == (123 << 12) | (5 << 9) | 39


def test_struct_unpacking():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    inst = TestStruct._pt_unpack((39 << 15) | (5 << 12) | 123)
    assert inst.ab.value == 123
    assert inst.cd.value == 5
    assert inst.ef.value == 39


def test_struct_unpacking_from_msb():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(packing=Packing.FROM_MSB)
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    inst = TestStruct._pt_unpack((123 << 12) | (5 << 9) | 39)
    assert inst.ab.value == 123
    assert inst.cd.value == 5
    assert inst.ef.value == 39


def test_struct_oversized():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(width=17)
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    with pytest.raises(WidthError) as e:
        TestStruct()

    assert str(e.value) == (
        "Fields of TestStruct total 24 bits which does not fit within the "
        "specified width of 17 bits"
    )


def test_struct_nested():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class Inner:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    @TestPkg.struct()
    class Outer:
        inner: Inner
        other: Scalar[7]

    # Packing
    packed = Outer()
    packed.inner.ab = 943
    packed.inner.cd = 1
    packed.inner.ef = 67
    packed.other = 29

    assert packed._pt_pack() == (29 << 24) | (67 << 15) | (1 << 12) | 943

    # Unpacking
    unpacked = Outer._pt_unpack((17 << 24) | (41 << 15) | (4 << 12) | 435)
    assert unpacked.inner.ab.value == 435
    assert unpacked.inner.cd.value == 4
    assert unpacked.inner.ef.value == 41
    assert unpacked.other.value == 17
