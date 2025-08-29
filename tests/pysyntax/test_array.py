# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import itertools
from random import choice, getrandbits

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
    @packtype.package()
    class TestPkg:
        # This will declare a Scalar[4] with dimensions 5x6x7
        multi : Scalar[4][5][6][7]

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
    @packtype.package()
    class Pkg1D:
        pass

    @Pkg1D.struct()
    class Struct1D:
        field_a : Scalar[1]
        field_b : Scalar[2]

    @Pkg1D.enum()
    class Enum1D:
        VAL_A : Constant
        VAL_B : Constant
        VAL_C : Constant

    @Pkg1D.union()
    class Union1D:
        raw : Scalar[3]
        struct : Struct1D

    @packtype.package()
    class Pkg2D:
        Struct2D : Struct1D[4]
        Enum2D : Enum1D[5]
        Union2D : Union1D[6]

    @packtype.package()
    class Pkg3D:
        Struct3D : Pkg2D.Struct2D[2]
        Enum3D : Pkg2D.Enum2D[3]
        Union3D : Pkg2D.Union2D[4]

    # === Check struct ===
    inst_struct = Pkg3D.Struct3D()
    assert inst_struct._pt_width ==  (1+2) * 4 * 2
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

