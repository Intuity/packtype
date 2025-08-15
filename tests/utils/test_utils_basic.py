# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math

import pytest

import packtype
from packtype import Constant, Scalar, utils

from ..fixtures import reset_registry

assert reset_registry


def test_utils_basic_clog2():
    for idx in range(1, 100):
        assert utils.clog2(idx) == math.ceil(math.log2(idx))


def test_utils_basic_get_width():
    @packtype.package()
    class TestPkg:
        simple_type: Scalar[8]

    assert utils.get_width(TestPkg.simple_type) == 8


def test_utils_basic_get_name():
    @packtype.package()
    class TestPkg:
        simple_type: Scalar[8]

    assert utils.get_name(TestPkg.simple_type) == "simple_type"


def test_utils_basic_get_doc():
    @packtype.package()
    class TestPkg:
        """My package docstring"""

    assert utils.get_doc(TestPkg) == "My package docstring"


def test_utils_basic_is_signed():
    @packtype.package()
    class TestPkg:
        sc_signed: Scalar[8, True]
        sc_unsigned: Scalar[8]

    assert utils.is_signed(TestPkg.sc_signed)
    assert not utils.is_signed(TestPkg.sc_unsigned)


def test_utils_basic_unpack_pack():
    @packtype.package()
    class TestPkg:
        sc_unsigned: Scalar[8]

    @TestPkg.struct()
    class TestStruct:
        a: Scalar[4]
        b: Scalar[4]

    @TestPkg.enum()
    class TestEnum:
        A: Constant = 0x1
        B: Constant = 0x2
        C: Constant = 0x3

    @TestPkg.union()
    class TestUnion:
        struct: TestStruct
        raw: Scalar[8]

    # Unpack a scalar
    inst_sc = utils.unpack(TestPkg.sc_unsigned, 123)
    assert isinstance(inst_sc, Scalar)
    assert inst_sc == 123
    assert isinstance(utils.pack(inst_sc), int)
    assert utils.pack(inst_sc) == 123

    # Unpack a struct
    inst_struct = utils.unpack(TestStruct, 0x48)
    assert isinstance(inst_struct, TestStruct)
    assert inst_struct.a == 0x8
    assert inst_struct.b == 0x4
    assert isinstance(utils.pack(inst_struct), int)
    assert utils.pack(inst_struct) == 0x48

    # Unpack an enum
    inst_enum = utils.unpack(TestEnum, 0x2)
    assert isinstance(inst_enum, TestEnum)
    assert inst_enum is TestEnum.B
    assert isinstance(utils.pack(inst_enum), int)
    assert utils.pack(inst_enum) == 0x2

    # Unpack an unknown enum value
    inst_enum_unknown = utils.unpack(TestEnum, 0)
    assert isinstance(inst_enum_unknown, TestEnum)
    assert inst_enum_unknown not in (TestEnum.A, TestEnum.B, TestEnum.C)
    assert int(inst_enum_unknown) == 0
    assert isinstance(utils.pack(inst_enum_unknown), int)
    assert utils.pack(inst_enum_unknown) == 0

    # Unpack a union
    inst_union = utils.unpack(TestUnion, 0x48)
    assert isinstance(inst_union, TestUnion)
    assert inst_union.raw == 0x48
    assert inst_union.struct.a == 0x8
    assert inst_union.struct.b == 0x4
    assert isinstance(utils.pack(inst_union), int)
    assert utils.pack(inst_union) == 0x48


def test_utils_basic_bad_unpack_pack():
    @packtype.package()
    class TestPkg:
        sc_unsigned: Scalar[8]

    @TestPkg.struct()
    class TestStruct:
        a: Scalar[4]
        b: Scalar[4]

    @TestPkg.enum()
    class TestEnum:
        A: Constant = 0x1
        B: Constant = 0x2
        C: Constant = 0x3

    @TestPkg.union()
    class TestUnion:
        struct: TestStruct
        raw: Scalar[8]

    # Scalar

    with pytest.raises(TypeError):
        utils.unpack(TestPkg.sc_unsigned(32), 123)

    with pytest.raises(TypeError):
        utils.pack(TestPkg.sc_unsigned)

    # Struct

    with pytest.raises(TypeError):
        utils.unpack(TestStruct(), 123)

    with pytest.raises(TypeError):
        utils.pack(TestStruct)

    # Enum

    with pytest.raises(TypeError):
        utils.unpack(TestEnum(), 123)

    with pytest.raises(TypeError):
        utils.pack(TestEnum)

    # Union

    with pytest.raises(TypeError):
        utils.unpack(TestUnion(), 123)

    with pytest.raises(TypeError):
        utils.pack(TestUnion)
