# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import copy
import math

import pytest
import tabulate

import packtype
from packtype import Constant, Scalar, utils
from packtype.types.scalar import ScalarType

from ..fixtures import reset_registry

assert reset_registry


def test_utils_basic_clog2():
    for idx in range(1, 100):
        assert utils.clog2(idx) == math.ceil(math.log2(idx))


def test_utils_basic_get_width():
    @packtype.package()
    class TestPkgA:
        simple_type: Scalar[8]

    @packtype.package()
    class TestPkgB:
        arrayed_type: TestPkgA.simple_type[4]

    assert utils.get_width(TestPkgA.simple_type) == 8
    assert utils.get_width(TestPkgB.arrayed_type) == 32


def test_utils_basic_get_name():
    @packtype.package()
    class TestPkg:
        simple_type: Scalar[8]

    assert utils.get_name(TestPkg.simple_type) == "simple_type"


def test_utils_bad_get_name():
    """Check that an error is raised for struct field name"""

    @packtype.package()
    class TestPkg:
        simple_type: Scalar[8]

    @TestPkg.struct()
    class TestStruct:
        field_a: TestPkg.simple_type[4]

    with pytest.raises(TypeError) as exc:
        struct = TestStruct()
        utils.get_name(struct.field_a)

    assert str(exc.value).startswith("Cannot determine a name for nested array spec")


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
    assert isinstance(inst_sc, ScalarType)
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


def test_utils_diff_scalar_table():
    """
    Test the diff tableing with the diff utility on scalars
    """

    @packtype.package()
    class TestPkg:
        sc_unsigned: Scalar[8]
        sc_small: Scalar[4]

    @TestPkg.enum()
    class TestEnum:
        A: Constant = 0x1
        B: Constant = 0x2
        C: Constant = 0x3

    a = TestPkg.sc_unsigned(42)
    b = TestPkg.sc_unsigned(42)
    c = TestPkg.sc_unsigned(84)
    enum_a = TestEnum.A
    enum_a2 = TestEnum.A
    enum_b = TestEnum.B

    assert utils.diff_table(a, b) == ""
    assert utils.diff_table(b, a) == ""
    assert utils.diff_table(enum_a, enum_a2) == ""
    diff_struct = {
        "Member name": ["sc_unsigned"],
        "Value A": [f"{42}\n0x{42:02X}"],
        "Value B": [f"{84}\n0x{84:02X}"],
        "Diff": ["Y"],
    }
    assert utils.diff(a, c) == diff_struct
    diff_struct_enum = {
        "Member name": ["TestEnum"],
        "Value A": [f"{enum_a}"],
        "Value B": [f"{enum_b}"],
        "Diff": ["Y"],
    }
    assert utils.diff(enum_a, enum_b) == diff_struct_enum
    # Check table can be properly rendered
    assert utils.diff_table(enum_a, enum_b) == tabulate.tabulate(
        diff_struct_enum,
        headers="keys",
        tablefmt="grid",
        colalign=("left", "center", "center", "center"),
    )


def test_utils_diff_struct():
    """Test the diff function with structs."""

    @packtype.package()
    class TestPkg:
        sc_unsigned: Scalar[8]

    @TestPkg.struct()
    class TestStruct:
        field_a: TestPkg.sc_unsigned
        field_b: TestPkg.sc_unsigned

    @TestPkg.struct()
    class TestStructOuter:
        inner: TestStruct
        field_c: TestPkg.sc_unsigned

    a = TestStruct(
        field_a=TestPkg.sc_unsigned(1),
        field_b=TestPkg.sc_unsigned(2),
    )
    b = TestStruct(
        field_a=TestPkg.sc_unsigned(1),
        field_b=TestPkg.sc_unsigned(3),
    )
    c = TestStructOuter(
        inner=b,
        field_c=TestPkg.sc_unsigned(4),
    )
    d = TestStructOuter(
        inner=a,
        field_c=TestPkg.sc_unsigned(5),
    )
    a_values = ["0x201", "0x2"]
    b_values = ["0x301", "0x3"]
    diff_ab = {
        "Member name": ["TestStruct", "TestStruct.field_b"],
        "Value A": [f"{int(v, 16)}\n{v}" for v in a_values],
        "Value B": [f"{int(v, 16)}\n{v}" for v in b_values],
        "Diff": ["Y", "Y"],
    }
    assert utils.diff(a, b) == diff_ab

    a_values = ["0x4_0301", "0x301", "0x3", "0x4"]
    b_values = ["0x5_0201", "0x201", "0x2", "0x5"]
    diff_cd = {
        "Member name": [
            "TestStructOuter",
            "TestStructOuter.inner",
            "TestStructOuter.inner.field_b",
            "TestStructOuter.field_c",
        ],
        "Value A": [f"{int(v, 16)}\n{v}" for v in a_values],
        "Value B": [f"{int(v, 16)}\n{v}" for v in b_values],
        "Diff": ["Y", "Y", "Y", "Y"],
    }
    # Check that tables can be properly rendered
    assert utils.diff(c, d) == diff_cd
    assert utils.diff_table(c, d) == tabulate.tabulate(
        diff_cd, headers="keys", tablefmt="grid", colalign=("left", "center", "center", "center")
    )


def test_utils_diff_arrays():
    """Test the diff function with arrays of structs."""

    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    @packtype.package()
    class TestPkg2:
        StructArray4: TestPkg.TestByte[4]
        MDimStructArray2x2: TestPkg.TestByte[2][2]

    a = utils.unpack(TestPkg2.StructArray4, 0x12_34_56_78)
    b = utils.unpack(TestPkg2.StructArray4, 0x12_34_56_79)

    a_values = ["0x1234_5678", "0x78", "0x8"]
    b_values = ["0x1234_5679", "0x79", "0x9"]
    diff_struct = {
        "Member name": ["StructArray4", "StructArray4[0]", "StructArray4[0].low"],
        "Value A": [f"{int(v, 16)}\n{v}" for v in a_values],
        "Value B": [f"{int(v, 16)}\n{v}" for v in b_values],
        "Diff": ["Y", "Y", "Y"],
    }
    assert utils.diff(a, b) == diff_struct

    a2d = utils.unpack(TestPkg2.MDimStructArray2x2, 0x12_34_56_78)
    b2d = utils.unpack(TestPkg2.MDimStructArray2x2, 0x13_34_57_78)
    a_values = ["0x1234_5678", "0x5678", "0x56", "0x6", "0x1234", "0x12", "0x2"]
    b_values = ["0x1334_5778", "0x5778", "0x57", "0x7", "0x1334", "0x13", "0x3"]
    diff_struct_2d = {
        "Member name": [
            "MDimStructArray2x2",
            "MDimStructArray2x2[0]",
            "MDimStructArray2x2[0][1]",
            "MDimStructArray2x2[0][1].low",
            "MDimStructArray2x2[1]",
            "MDimStructArray2x2[1][1]",
            "MDimStructArray2x2[1][1].low",
        ],
        "Value A": [f"{int(v, 16)}\n{v}" for v in a_values],
        "Value B": [f"{int(v, 16)}\n{v}" for v in b_values],
        "Diff": ["Y", "Y", "Y", "Y", "Y", "Y", "Y"],
    }

    assert utils.diff(a2d, b2d) == diff_struct_2d
    # Check that tables can be properly rendered
    assert utils.diff_table(a2d, b2d) == tabulate.tabulate(
        diff_struct_2d,
        headers="keys",
        tablefmt="grid",
        colalign=("left", "center", "center", "center"),
    )


def test_utils_diff_unions():
    """Test the diff function with unions."""

    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    @TestPkg.union()
    class TestUnion:
        struct: TestByte
        pair: TestPkg.nibble[2]
        raw: Scalar[8]

    a = utils.unpack(TestUnion, 0x12)
    b = utils.unpack(TestUnion, 0x13)
    a_values = ["0x12", "0x12", "0x2", "0x12", "0x2", "0x12"]
    b_values = ["0x13", "0x13", "0x3", "0x13", "0x3", "0x13"]
    diff_struct = {
        "Member name": [
            "TestUnion",
            "TestUnion.struct",
            "TestUnion.struct.low",
            "TestUnion.pair",
            "TestUnion.pair[0]",
            "TestUnion.raw",
        ],
        "Value A": [f"{int(v, 16)}\n{v}" for v in a_values],
        "Value B": [f"{int(v, 16)}\n{v}" for v in b_values],
        "Diff": ["Y", "Y", "Y", "Y", "Y", "Y"],
    }
    assert utils.diff(a, b) == diff_struct


def test_copy_enum():
    """
    Test copying an enum instance
    """

    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.enum()
    class TestEnum:
        A: Constant = 0x1
        B: Constant = 0x2
        C: Constant = 0x3

    enum_a = TestEnum.A
    enum_a_copy = copy.copy(enum_a)
    assert enum_a == enum_a_copy
    enum_a += 1
    assert enum_a != enum_a_copy


def test_copy_struct():
    """
    Test that the util function works for structs
    """

    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    struct_a = utils.unpack(TestByte, 0xFF)
    struct_a_copy = copy.copy(struct_a)
    struct_a_equals = struct_a
    assert struct_a == struct_a_copy == struct_a_copy
    # Mutate original struct a
    struct_a.low = 0x0
    assert struct_a_equals == struct_a
    assert struct_a_copy != struct_a


def test_copy_union():
    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    @TestPkg.union()
    class TestUnion:
        struct: TestByte
        raw: Scalar[8]

    union_a = utils.unpack(TestUnion, 0xFF)
    union_a_copy = copy.copy(union_a)
    union_a_equals = union_a
    assert union_a == union_a_copy == union_a_copy
    # Mutate original struct a
    union_a.struct.low = 0x0
    assert union_a_equals == union_a
    assert union_a_copy != union_a


def test_copy_array():
    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    @packtype.package()
    class ArrayPkg:
        ByteArray: TestPkg.TestByte[4]
        Byte2DArray: TestPkg.TestByte[2][2]

    byte_array = utils.unpack(ArrayPkg.ByteArray, 0x12345678)
    byte_2d_array = utils.unpack(ArrayPkg.Byte2DArray, 0x12345678)

    byte_array_equals = byte_array
    byte_array_copy = copy.copy(byte_array)
    assert byte_array is not byte_array_copy
    assert byte_array == byte_array_copy == byte_array_equals

    byte_2d_array_equals = byte_2d_array
    byte_2d_array_copy = copy.copy(byte_2d_array)
    assert byte_2d_array is not byte_2d_array_copy
    assert byte_2d_array == byte_2d_array_copy == byte_2d_array_equals

    # Mutate arrays
    byte_array[0] = 0x00
    byte_2d_array[1][0] = 0x00

    assert byte_array == byte_array_equals
    assert byte_array != byte_array_copy

    assert byte_2d_array == byte_2d_array_equals
    assert byte_2d_array_copy != byte_2d_array


def test_deepcopy_enum():
    """
    Test deep copying an enum instance
    """

    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.enum()
    class TestEnum:
        A: Constant = 0x1
        B: Constant = 0x2
        C: Constant = 0x3

    enum_a = TestEnum.A
    enum_a_deepcopy = copy.deepcopy(enum_a)
    assert enum_a == enum_a_deepcopy
    enum_a += 1
    assert enum_a != enum_a_deepcopy


def test_deepcopy_struct():
    """
    Test that deepcopy works for structs
    """

    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    struct_a = utils.unpack(TestByte, 0xFF)
    struct_a_deepcopy = copy.deepcopy(struct_a)
    struct_a_equals = struct_a
    assert struct_a == struct_a_deepcopy == struct_a_equals
    # Mutate original struct a
    struct_a.low = 0x0
    assert struct_a_equals == struct_a
    assert struct_a_deepcopy != struct_a


def test_deepcopy_union():
    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    @TestPkg.union()
    class TestUnion:
        struct: TestByte
        raw: Scalar[8]

    union_a = utils.unpack(TestUnion, 0xFF)
    union_a_deepcopy = copy.deepcopy(union_a)
    union_a_equals = union_a
    assert union_a == union_a_deepcopy == union_a_equals
    # Mutate original struct a
    union_a.struct.low = 0x0
    assert union_a_equals == union_a
    assert union_a_deepcopy != union_a


def test_deepcopy_array():
    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    @packtype.package()
    class ArrayPkg:
        ByteArray: TestPkg.TestByte[4]
        Byte2DArray: TestPkg.TestByte[2][2]

    byte_array = utils.unpack(ArrayPkg.ByteArray, 0x12345678)
    byte_2d_array = utils.unpack(ArrayPkg.Byte2DArray, 0x12345678)

    byte_array_equals = byte_array
    byte_array_deepcopy = copy.deepcopy(byte_array)
    assert byte_array is not byte_array_deepcopy
    assert byte_array == byte_array_deepcopy == byte_array_equals

    byte_2d_array_equals = byte_2d_array
    byte_2d_array_deepcopy = copy.deepcopy(byte_2d_array)
    assert byte_2d_array is not byte_2d_array_deepcopy
    assert byte_2d_array == byte_2d_array_deepcopy == byte_2d_array_equals

    # Mutate arrays
    byte_array[0] = 0x00
    byte_2d_array[1][0] = 0x00

    assert byte_array == byte_array_equals
    assert byte_array != byte_array_deepcopy

    assert byte_2d_array == byte_2d_array_equals
    assert byte_2d_array_deepcopy != byte_2d_array


def test_deepcopy_unpacked_array():
    @packtype.package()
    class TestPkg:
        nibble: Scalar[4]

    @TestPkg.struct()
    class TestByte:
        low: TestPkg.nibble
        high: TestPkg.nibble

    @packtype.package()
    class ArrayPkg:
        ByteArray: TestPkg.TestByte[4]

    byte_array_spec = ArrayPkg.ByteArray
    unpacked_array = byte_array_spec.as_unpacked()

    # Set some initial values
    unpacked_array[0] = utils.unpack(TestByte, 0x12)
    unpacked_array[1] = utils.unpack(TestByte, 0x34)
    unpacked_array[2] = utils.unpack(TestByte, 0x56)
    unpacked_array[3] = utils.unpack(TestByte, 0x78)

    unpacked_array_equals = unpacked_array
    unpacked_array_deepcopy = copy.deepcopy(unpacked_array)
    assert unpacked_array is not unpacked_array_deepcopy
    assert unpacked_array[0] == unpacked_array_deepcopy[0]
    assert unpacked_array[1] == unpacked_array_deepcopy[1]
    assert unpacked_array[2] == unpacked_array_deepcopy[2]
    assert unpacked_array[3] == unpacked_array_deepcopy[3]

    # Mutate original array
    unpacked_array[0] = utils.unpack(TestByte, 0x00)
    unpacked_array[1] = utils.unpack(TestByte, 0x00)

    assert unpacked_array[0] == unpacked_array_equals[0]
    assert unpacked_array[1] == unpacked_array_equals[1]
    assert unpacked_array[0] != unpacked_array_deepcopy[0]
    assert unpacked_array[1] != unpacked_array_deepcopy[1]
    assert unpacked_array[2] == unpacked_array_deepcopy[2]
    assert unpacked_array[3] == unpacked_array_deepcopy[3]
