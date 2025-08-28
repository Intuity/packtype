# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

import packtype
from packtype import Constant, Packing, Scalar
from packtype.types.assembly import AssignmentError, WidthError
from packtype.types.primitive import PrimitiveValueError
from packtype.types.wrap import BadAssignmentError, BadAttributeError

from ..fixtures import reset_registry

assert reset_registry


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

    assert (inst._pt_lsb("ab"), inst._pt_msb("ab")) == (0, 11)
    assert (inst._pt_lsb("cd"), inst._pt_msb("cd")) == (12, 14)
    assert (inst._pt_lsb("ef"), inst._pt_msb("ef")) == (15, 23)


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

    with pytest.raises(WidthError) as e:

        @TestPkg.struct(width=17)
        class TestStruct:
            ab: Scalar[12]
            cd: Scalar[3]
            ef: Scalar[9]

    assert str(e.value) == (
        "Fields of TestStruct total 24 bits which does not fit within the "
        "specified width of 17 bits"
    )


def test_struct_oversized_value():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    with pytest.raises(PrimitiveValueError) as e:
        inst = TestStruct()
        inst.ab = 0x1234

    assert str(e.value) == "Value 4660 cannot be represented by 12 bits"


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


def test_struct_bad_assign():
    @packtype.package()
    class TestPkg:
        pass

    with pytest.raises(BadAssignmentError) as e:

        @TestPkg.struct()
        class TestStruct:
            ab: Scalar[12] = 123

    assert (
        str(e.value)
        == "TestStruct.ab cannot be assigned an initial value of 123 within a base type of Struct"
    )


def test_struct_bad_get_width():
    @packtype.package()
    class TestPkg:
        pass

    with pytest.raises(BadAttributeError) as e:

        @TestPkg.struct(width=-5)
        class TestStruct:
            ab: Scalar[12]

    assert str(e.value) == "Unsupported value '-5' for attribute 'width' for Struct"


def test_struct_lookup():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]
        gh: Scalar[9]

    inst = TestStruct()
    assert inst._pt_lookup(inst.ab) == "ab"
    assert inst._pt_lookup(inst.cd) == "cd"
    assert inst._pt_lookup(inst.ef) == "ef"
    assert inst._pt_lookup(inst.gh) == "gh"


def test_struct_fields_listing():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3]
        ef: Scalar[9]

    inst = TestStruct()

    # LSB -> MSB
    assert list(inst._pt_fields_lsb_asc) == [
        (0, 11, ("ab", inst.ab)),
        (12, 14, ("cd", inst.cd)),
        (15, 23, ("ef", inst.ef)),
    ]

    # MSB -> LSB
    assert list(inst._pt_fields_msb_desc) == [
        (15, 23, ("ef", inst.ef)),
        (12, 14, ("cd", inst.cd)),
        (0, 11, ("ab", inst.ab)),
    ]


def test_struct_enum():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(width=16)
    class TestEnum:
        A: Constant = 0x1234
        B: Constant = 0x2345
        C: Constant = 0x3456

    @TestPkg.struct()
    class TestStruct:
        a: Scalar[2]
        b: TestEnum
        c: Scalar[3]

    # Packing
    inst = TestStruct()
    inst.a = 2
    inst.b = 0x1234
    inst.c = 7
    assert int(inst.a) == 2
    assert int(inst.b) == 0x1234
    assert int(inst.c) == 7
    assert inst._pt_pack() == ((7 << 18) | (0x1234 << 2) | 2)
    assert int(inst) == ((7 << 18) | (0x1234 << 2) | 2)

    # Unpacking
    inst = TestStruct._pt_unpack((7 << 18) | (0x1234 << 2) | 2)
    assert int(inst.a) == 2
    assert int(inst.b) == 0x1234
    assert int(inst.c) == 7


def test_struct_constructor():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class InnerA:
        ab: Scalar[6]
        cd: Scalar[2]

    @TestPkg.struct()
    class InnerB:
        ab: Scalar[2]
        cd: Scalar[6]

    @TestPkg.union()
    class InnerUnion:
        a: InnerA
        b: InnerB

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3][3]
        ef: Scalar[9]
        gh: InnerUnion

    inst = TestStruct(ab=123, cd=[4, 5, 6], ef=41, gh=0x27)
    assert int(inst.ab) == 123
    assert int(inst.cd[0]) == 4
    assert int(inst.cd[1]) == 5
    assert int(inst.cd[2]) == 6
    assert int(inst.ef) == 41
    assert int(inst.gh) == 0x27
    assert int(inst.gh.a) == 0x27
    assert int(inst.gh.a.ab) == (0x27 & 0x3F)
    assert int(inst.gh.a.cd) == (0x27 & 0xC0) >> 6
    assert int(inst.gh.b) == 0x27
    assert int(inst.gh.b.ab) == (0x27 & 0x03)
    assert int(inst.gh.b.cd) == (0x27 & 0xFC) >> 2


def test_struct_bad_constructor():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3][3]
        ef: Scalar[9]

    # Test a single value being assigned to an array
    with pytest.raises(AssignmentError) as e:
        TestStruct(ab=123, cd=4, ef=41)

    assert str(e.value) == (
        "Cannot assign value to field cd as it is an array of 3 entries and the "
        "assigned value does not have the same dimensions"
    )

    # Test assigning an array that's too small
    with pytest.raises(AssignmentError) as e:
        TestStruct(ab=123, cd=[4, 5], ef=41)

    assert str(e.value) == (
        "Cannot assign value to field cd as it is an array of 3 entries and the "
        "assigned value does not have the same dimensions"
    )

    # Check that extra field is flagged
    with pytest.raises(AssignmentError) as e:
        TestStruct(ab=123, cd=[4, 5, 6], ef=41, gh=3)

    assert str(e.value) == "TestStruct does not contain a field called 'gh'"
