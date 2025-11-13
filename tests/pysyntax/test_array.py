# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import itertools
from random import choice, getrandbits

import packtype
from packtype import Constant, Packing, Scalar
from packtype.utils import pack, unpack

from ..fixtures import reset_registry

assert reset_registry


def test_array():
    @packtype.package()
    class TestPkg:
        EF_NUM: Constant = 2

    @TestPkg.struct()
    class TestStruct:
        ab: Scalar[12]
        cd: Scalar[3][3]
        ef: Scalar[9][TestPkg.EF_NUM]

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
        cd: Scalar[3][3]
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
        cd: Scalar[3][3]
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
        cd: Scalar[3][3]
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
        cd: Scalar[3][3]
        ef: Scalar[9]

    inst = TestStruct._pt_unpack((123 << 18) | (1 << 15) | (2 << 12) | (3 << 9) | 53)
    assert int(inst.ab) == 123
    assert int(inst.cd[0]) == 1
    assert int(inst.cd[1]) == 2
    assert int(inst.cd[2]) == 3
    assert int(inst.ef) == 53


def test_array_multidimensional_scalar():
    """Basic test that a multi-dimensional scalar value can be declared"""

    @packtype.package()
    class TestPkg:
        # This will declare a Scalar[4] with dimensions 5x6x7
        multi: Scalar[4][5][6][7]

    inst = TestPkg.multi()
    # Check size and dimensions
    assert inst._pt_width == 4 * 5 * 6 * 7
    assert len(inst) == 7
    assert len(inst[0]) == 6
    assert len(inst[0][0]) == 5
    # Write in data
    ref = {}
    raw = 0
    for x, y, z in itertools.product(range(7), range(6), range(5)):
        ref[x, y, z] = getrandbits(4)
        raw |= ref[x, y, z] << ((x * 6 * 5 * 4) + (y * 5 * 4) + (z * 4))
        inst[x][y][z] = ref[x, y, z]
    # Check persistance
    for x, y, z in itertools.product(range(7), range(6), range(5)):
        assert inst[x][y][z] == ref[x, y, z]
    # Check overall value
    assert int(inst) == raw


def test_array_multidimensional_rich():
    """Test that multi-dimensional structs, enums, and unions can be declared"""

    @packtype.package()
    class Pkg1D:
        pass

    @Pkg1D.struct()
    class Struct1D:
        field_a: Scalar[1]
        field_b: Scalar[2]

    @Pkg1D.enum()
    class Enum1D:
        VAL_A: Constant
        VAL_B: Constant
        VAL_C: Constant

    @Pkg1D.union()
    class Union1D:
        raw: Scalar[3]
        struct: Struct1D

    @packtype.package()
    class Pkg2D:
        Struct2D: Struct1D[4]
        Enum2D: Enum1D[5]
        Union2D: Union1D[6]

    @packtype.package()
    class Pkg3D:
        Struct3D: Pkg2D.Struct2D[2]
        Enum3D: Pkg2D.Enum2D[3]
        Union3D: Pkg2D.Union2D[4]

    # === Check struct ===
    inst_struct = Pkg3D.Struct3D()
    assert inst_struct._pt_width == (1 + 2) * 4 * 2
    assert len(inst_struct) == 2
    assert len(inst_struct[0]) == 4

    # Write in data
    ref = {}
    raw = 0
    for x, y in itertools.product(range(2), range(4)):
        ref[x, y] = (a := getrandbits(1)), (b := getrandbits(2))
        raw |= (a | (b << 1)) << ((x * 4 * 3) + (y * 3))
        inst_struct[x][y].field_a = a
        inst_struct[x][y].field_b = b

    # Check persistance
    for x, y in itertools.product(range(2), range(4)):
        assert inst_struct[x][y].field_a == ref[x, y][0]
        assert inst_struct[x][y].field_b == ref[x, y][1]

    # Check overall value
    assert int(inst_struct) == raw

    # === Check enum ===
    inst_enum = Pkg3D.Enum3D()
    assert inst_enum._pt_width == 2 * 5 * 3
    assert len(inst_enum) == 3
    assert len(inst_enum[0]) == 5

    # Write in data
    ref = {}
    raw = 0
    for x, y in itertools.product(range(3), range(5)):
        ref[x, y] = choice((Enum1D.VAL_A, Enum1D.VAL_B, Enum1D.VAL_C))
        raw |= ref[x, y] << ((x * 5 * 2) + (y * 2))
        inst_enum[x][y] = ref[x, y]

    # Check persistance
    for x, y in itertools.product(range(3), range(5)):
        assert inst_enum[x][y] == ref[x, y]

    # Check overall value
    assert int(inst_enum) == raw

    # === Check union ===
    inst_union = Pkg3D.Union3D()
    assert inst_union._pt_width == 3 * 6 * 4
    assert len(inst_union) == 4
    assert len(inst_union[0]) == 6

    # Write in data
    ref = {}
    raw = 0
    for x, y in itertools.product(range(4), range(6)):
        ref[x, y] = getrandbits(3)
        raw |= ref[x, y] << ((x * 6 * 3) + (y * 3))
        inst_union[x][y].raw = ref[x, y]

    # Check persistance
    for x, y in itertools.product(range(4), range(6)):
        assert inst_union[x][y].raw == ref[x, y]
        assert inst_union[x][y].struct == ref[x, y]

    # Check overall value
    assert int(inst_union) == raw


def test_array_multidimensional_struct_field():
    """Test that structs can have multi-dimensional fields"""

    @packtype.package()
    class TestPkg:
        Scalar3D: Scalar[2][3][4]

    @TestPkg.struct()
    class TestStruct:
        field_a: TestPkg.Scalar3D
        field_b: Scalar[3][4][5]

    inst = TestStruct()
    assert inst._pt_width == (2 * 3 * 4) + (3 * 4 * 5)
    inst.field_a = (data_a := getrandbits(2 * 3 * 4))
    inst.field_b = (data_b := getrandbits(3 * 4 * 5))
    assert int(inst.field_a) == data_a
    assert int(inst.field_b) == data_b
    assert int(inst) == data_a | (data_b << (2 * 3 * 4))
    for x, y in itertools.product(range(4), range(3)):
        assert inst.field_a[x][y] == (data_a >> ((x * 3 * 2) + (y * 2))) & 0b11
    for x, y in itertools.product(range(5), range(4)):
        assert inst.field_b[x][y] == (data_b >> ((x * 4 * 3) + (y * 3))) & 0b111


def test_array_multidimensional_union_member():
    """Test that unions can have multi-dimensional field members"""

    @packtype.package()
    class TestPkg:
        Scalar3D: Scalar[2][3][4]

    @TestPkg.union()
    class TestUnion:
        member_a: TestPkg.Scalar3D
        member_b: Scalar[2 * 3 * 4]

    inst = TestUnion()
    assert inst._pt_width == 2 * 3 * 4
    inst.member_a = (data_a := getrandbits(2 * 3 * 4))
    assert int(inst.member_a) == data_a
    assert int(inst.member_b) == data_a
    assert int(inst) == data_a
    for x, y in itertools.product(range(4), range(3)):
        assert inst.member_a[x][y] == (data_a >> ((x * 3 * 2) + (y * 2))) & 0b11


def test_array_struct_comparison():
    """Test that arrays of structs and unions can be compared"""

    @packtype.package()
    class TestPkg:
        a_nibble: Scalar[4]

    @TestPkg.struct()
    class ExampleStruct:
        nibble_a: TestPkg.a_nibble
        nibble_b: Scalar[4]
        byte_a: Scalar[8]

    @TestPkg.union()
    class ExampleUnion:
        raw: Scalar[16]
        struct: ExampleStruct

    @TestPkg.struct()
    class UnwrappedStructArray:
        idx_0: TestPkg.ExampleStruct
        idx_1: TestPkg.ExampleStruct
        idx_2: TestPkg.ExampleStruct
        idx_3: TestPkg.ExampleStruct

    @packtype.package()
    class TestPkg2:
        StructArray: TestPkg.ExampleStruct[4]
        UnionArray: TestPkg.ExampleUnion[4]

    test_value = 0x0123456789ABCDEF  # 64 bit value to pack
    value_a = unpack(TestPkg.UnwrappedStructArray, test_value)
    value_b = unpack(TestPkg2.StructArray, test_value)
    assert pack(value_a) == pack(value_b)
    assert value_a.idx_0 == value_b[0]
    assert value_a.idx_1 == value_b[1]
    assert value_a.idx_2 == value_b[2]
    assert value_a.idx_3 == value_b[3]

    value_c = unpack(TestPkg2.StructArray, test_value)
    value_d = unpack(TestPkg2.UnionArray, test_value)
    assert value_d == value_c


def test_array_struct_str():
    """Test that arrays of structs print correctly"""

    @packtype.package()
    class TestPkg:
        a_nibble: Scalar[4]

    @TestPkg.struct()
    class ExampleStruct:
        nibble_a: TestPkg.a_nibble
        nibble_b: Scalar[4]
        byte_a: Scalar[8]

    @TestPkg.union()
    class ExampleUnion:
        raw: Scalar[16]
        struct: ExampleStruct

    @packtype.package()
    class TestPkg2:
        StructArray: TestPkg.ExampleStruct[4]
        UnionArray: TestPkg.ExampleUnion[2]

    test_value = 0x0123456789ABCDEF  # 64 bit value to pack
    value = unpack(TestPkg2.StructArray, test_value)
    assert str(value) == (
        f"PackedArray - 4 entries: 0x{test_value:X}\n"
        f"- Entry[0]: ExampleStruct: 0x{0xCDEF:X}\n"
        f"  [15: 8] ├─ byte_a   = 0xCD\n"
        f"  [ 7: 4] ├─ nibble_b = 0xE\n"
        f"  [ 3: 0] └─ nibble_a = 0xF\n"
        f"- Entry[1]: ExampleStruct: 0x{0x89AB:X}\n"
        f"  [15: 8] ├─ byte_a   = 0x89\n"
        f"  [ 7: 4] ├─ nibble_b = 0xA\n"
        f"  [ 3: 0] └─ nibble_a = 0xB\n"
        f"- Entry[2]: ExampleStruct: 0x{0x4567:X}\n"
        f"  [15: 8] ├─ byte_a   = 0x45\n"
        f"  [ 7: 4] ├─ nibble_b = 0x6\n"
        f"  [ 3: 0] └─ nibble_a = 0x7\n"
        f"- Entry[3]: ExampleStruct: 0x{0x123:X}\n"
        f"  [15: 8] ├─ byte_a   = 0x01\n"
        f"  [ 7: 4] ├─ nibble_b = 0x2\n"
        f"  [ 3: 0] └─ nibble_a = 0x3"
    )

    assert str(unpack(TestPkg2.UnionArray, 0x01234567)) == (
        f"PackedArray - 2 entries: 0x{0x01234567:X}\n"
        f"- Entry[0]: ExampleUnion: 0x{0x4567:X} (union):\n"
        f" |- raw    -> Unsigned Scalar[16]: 0x{0x4567:X}\n"
        f" |- struct -> ExampleStruct: 0x{0x4567:X}\n"
        f"                [15: 8] ├─ byte_a   = 0x45\n"
        f"                [ 7: 4] ├─ nibble_b = 0x6\n"
        f"                [ 3: 0] └─ nibble_a = 0x7\n"
        f"- Entry[1]: ExampleUnion: 0x{0x123:X} (union):\n"
        f" |- raw    -> Unsigned Scalar[16]: 0x{0x123:04X}\n"
        f" |- struct -> ExampleStruct: 0x{0x123:X}\n"
        f"                [15: 8] ├─ byte_a   = 0x01\n"
        f"                [ 7: 4] ├─ nibble_b = 0x2\n"
        f"                [ 3: 0] └─ nibble_a = 0x3"
    )
