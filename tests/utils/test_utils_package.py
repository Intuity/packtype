# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Alias, Constant, Scalar, utils

from ..fixtures import reset_registry

assert reset_registry


def test_utils_package_get_imports():
    @packtype.package()
    class PackageA:
        type_a: Scalar[8]

    @packtype.package()
    class PackageB:
        type_b: Alias[PackageA.type_a]

    assert list(utils.package.get_imports(PackageA)) == []
    assert list(utils.package.get_imports(PackageB)) == [("PackageA", "type_a")]


def test_utils_package_get_constants():
    @packtype.package()
    class PackageA:
        VALUE_A: Constant = 123
        VALUE_B: Constant = 456

    consts = list(utils.package.get_constants(PackageA))
    assert consts[0][0] == "VALUE_A"
    assert consts[0][1] == 123
    assert consts[1][0] == "VALUE_B"
    assert consts[1][1] == 456


def test_utils_package_get_scalars():
    @packtype.package()
    class PackageA:
        scalar_a: Scalar[8]
        scalar_b: Scalar[16]

    scalars = list(utils.package.get_scalars(PackageA))
    assert scalars[0][0] == "scalar_a"
    assert utils.get_width(scalars[0][1]) == 8
    assert scalars[1][0] == "scalar_b"
    assert utils.get_width(scalars[1][1]) == 16


def test_utils_package_get_enums():
    @packtype.package()
    class PackageA:
        pass

    @PackageA.enum()
    class EnumA:
        A: Constant
        B: Constant

    enums = list(utils.package.get_enums(PackageA))
    assert enums[0][0] == "EnumA"
    assert enums[0][1].A == 0
    assert enums[0][1].B == 1


def test_utils_package_get_structs_and_unions():
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

    types = list(utils.package.get_structs_and_unions(PackageA))
    assert len(types) == 2
    assert types[0][0] == "StructA"
    assert types[0][1] is StructA
    assert types[1][0] == "UnionA"
    assert types[1][1] is UnionA
