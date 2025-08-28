# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import itertools
from random import getrandbits

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


def test_array_multidimensional():
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
