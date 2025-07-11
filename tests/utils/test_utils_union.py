# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Scalar, utils

from ..fixtures import reset_registry

assert reset_registry


def test_utils_union_is_union():
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

    assert not utils.union.is_union(StructA)
    assert utils.union.is_union(UnionA)


def test_utils_union_get_members():
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

    members = list(utils.union.get_members(UnionA))
    assert members[0][0] == "raw"
    assert utils.get_width(members[0][1]) == utils.get_width(StructA)
    assert members[1][0] == "struct_a"
    assert utils.struct.is_struct(members[1][1])


def test_utils_union_is_simple_member():
    @packtype.package()
    class PackageA:
        some_type: Scalar[8]

    @PackageA.union()
    class UnionA:
        raw: Scalar[8]
        ref: PackageA.some_type

    union = UnionA()
    assert utils.union.is_simple_member(union.raw)
    assert not utils.union.is_simple_member(union.ref)


def test_utils_union_get_member_type():
    @packtype.package()
    class PackageA:
        some_type: Scalar[8]

    @PackageA.union()
    class UnionA:
        raw: Scalar[8]
        ref: PackageA.some_type

    union = UnionA()
    assert utils.union.get_member_type(union.raw) is None
    assert utils.union.get_member_type(union.ref) == "some_type"
