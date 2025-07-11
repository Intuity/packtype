# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Scalar, utils

from ..fixtures import reset_registry

assert reset_registry


def test_utils_struct_is_struct():
    @packtype.package()
    class PackageA:
        pass

    @PackageA.struct()
    class StructA:
        field_a: Scalar[8]
        field_b: Scalar[16]

    @PackageA.union()
    class UnionA:
        raw: Scalar[utils.get_width(StructA)]
        struct_a: StructA

    assert utils.struct.is_struct(StructA)
    assert not utils.struct.is_struct(UnionA)


def test_utils_struct_get_fields_msb_desc():
    @packtype.package()
    class PackageA:
        pass

    @PackageA.struct()
    class StructA:
        field_a: Scalar[8]
        field_b: Scalar[16]

    fields = list(utils.struct.get_fields_msb_desc(StructA))
    assert fields[0][0] == 8
    assert fields[0][1] == 23
    assert fields[0][2][0] == "field_b"

    assert fields[1][0] == 0
    assert fields[1][1] == 7
    assert fields[1][2][0] == "field_a"


def test_utils_struct_get_fields_lsb_asc():
    @packtype.package()
    class PackageA:
        pass

    @PackageA.struct()
    class StructA:
        field_a: Scalar[8]
        field_b: Scalar[16]

    fields = list(utils.struct.get_fields_lsb_asc(StructA))
    assert fields[0][0] == 0
    assert fields[0][1] == 7
    assert fields[0][2][0] == "field_a"

    assert fields[1][0] == 8
    assert fields[1][1] == 23
    assert fields[1][2][0] == "field_b"


def test_utils_struct_is_simple_field():
    @packtype.package()
    class PackageA:
        some_type: Scalar[8]

    @PackageA.struct()
    class StructA:
        field_a: Scalar[8]
        field_b: PackageA.some_type

    struct = StructA()
    assert utils.struct.is_simple_field(struct.field_a)
    assert not utils.struct.is_simple_field(struct.field_b)


def test_utils_struct_get_field_type():
    @packtype.package()
    class PackageA:
        some_type: Scalar[8]

    @PackageA.struct()
    class StructA:
        field_a: Scalar[8]
        field_b: PackageA.some_type

    struct = StructA()
    assert utils.struct.get_field_type(struct.field_a) is None
    assert utils.struct.get_field_type(struct.field_b) == "some_type"
