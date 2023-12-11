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
from packtype import Constant, Scalar
from packtype.union import UnionError

from ..fixtures import reset_registry

assert reset_registry


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


def test_union_nested():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(width=3)
    class EnumA:
        A: Constant
        B: Constant
        C: Constant

    @TestPkg.struct()
    class StructA:
        a: Scalar[10]
        b: EnumA

    @TestPkg.struct(width=13)
    class StructB:
        a: Scalar[5]
        # Deliberately missing to force padding

    @TestPkg.union()
    class UnionA:
        a: StructA
        b: StructB
        c: Scalar[13]

    @TestPkg.union()
    class UnionB:
        a: UnionA
        b: Scalar[13]

    # Packing
    inst = UnionB()
    inst.a.b = 142
    assert int(inst.a.a) == 142
    assert int(inst.a.b) == 142
    assert int(inst.a.c) == 142
    assert int(inst.b) == 142
    assert inst._pt_pack() == 142

    # Unpacking
    inst = UnionB._pt_unpack(142)
    assert int(inst.a.a) == 142
    assert int(inst.a.b) == 142
    assert int(inst.a.c) == 142
    assert int(inst.b) == 142

    # Repacking
    assert inst.a._pt_pack() == 142


def test_union_struct():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(width=32)
    class Header:
        address: Scalar[16]
        length: Scalar[8]
        mode: Scalar[4]
        flags: Scalar[4]

    @TestPkg.union()
    class Packet:
        raw: Scalar[32]
        header: Header

    inst = Packet()
    inst.header.address = 0x1234
    inst.header.length = 0x75
    inst.header.mode = 0x5
    inst.header.flags = 0x7
    assert int(inst.header.address) == 0x1234
    assert int(inst.header.length) == 0x75
    assert int(inst.header.mode) == 0x5
    assert int(inst.header.flags) == 0x7
    assert int(inst.raw) == (0x7 << 28) | (0x5 << 24) | (0x75 << 16) | 0x1234


def test_union_unpack():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct(width=32)
    class Header:
        address: Scalar[16]
        length: Scalar[8]
        mode: Scalar[4]
        flags: Scalar[4]

    @TestPkg.union()
    class Packet:
        raw: Scalar[32]
        header: Header

    inst = Packet._pt_unpack((0x7 << 28) | (0x5 << 24) | (0x75 << 16) | 0x1234)
    assert int(inst.raw) == (0x7 << 28) | (0x5 << 24) | (0x75 << 16) | 0x1234
    assert int(inst.header.address) == 0x1234
    assert int(inst.header.length) == 0x75
    assert int(inst.header.mode) == 0x5
    assert int(inst.header.flags) == 0x7


def test_union_bad_widths():
    @packtype.package()
    class TestPkg:
        pass

    with pytest.raises(UnionError) as e:
        @TestPkg.union()
        class TestUnion:
            a: Scalar[12]
            b: Scalar[11]

    assert str(e.value) == (
        "Union member b has a width of 11 that differs from the expected width " "of 12"
    )


def test_union_mismatches():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.union()
    class TestUnion:
        a: Scalar[12]
        b: Scalar[12]

    with pytest.raises(UnionError) as e:
        inst = TestUnion._pt_unpack(0x23)
        inst.a._Primitive__value = 0x17
        inst._pt_pack()

    assert str(e.value) == (
        "Multiple member values were discovered when packing a TestUnion union "
        "- expected a value of 0x23 but saw 0x23, 0x17"
    )


def test_union_functions():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class Form0:
        form: Scalar[1]
        data_a: Scalar[4]
        data_b: Scalar[8]

    @TestPkg.struct()
    class Form1:
        form: Scalar[1]
        data_a: Scalar[8]
        data_b: Scalar[4]

    @TestPkg.union()
    class TestUnion:
        f0: Form0
        f1: Form1

        def get_a(self):
            return self.f1.data_a if int(self.f0.form) == 1 else self.f0.data_a

        def get_b(self):
            return self.f1.data_b if int(self.f0.form) == 1 else self.f0.data_b

    inst_0 = TestUnion()
    inst_0.f0.form = 0
    inst_0.f0.data_a = 0x4
    inst_0.f0.data_b = 0x73

    inst_1 = TestUnion()
    inst_1.f1.form = 1
    inst_1.f1.data_a = 0x51
    inst_1.f1.data_b = 0x9

    assert int(inst_0.get_a()) == 0x4
    assert int(inst_0.get_b()) == 0x73
    assert int(inst_1.get_a()) == 0x51
    assert int(inst_1.get_b()) == 0x9
