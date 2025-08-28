# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

import packtype
from packtype import Constant, Scalar
from packtype.types.package import Package
from packtype.types.wrap import BadAttributeError, BadFieldTypeError, MissingAnnotationError

from ..fixtures import reset_registry

assert reset_registry


def test_package_decl():
    @packtype.package()
    class TestPkg:
        pass

    assert issubclass(TestPkg, Package)


def test_package_constants():
    @packtype.package()
    class TestPkg:
        A: Constant = 123
        B: Constant = 234

    assert TestPkg.A.value == 123
    assert int(TestPkg.A) == 123
    assert TestPkg.B.value == 234
    assert int(TestPkg.B) == 234


def test_package_unannotated():
    with pytest.raises(MissingAnnotationError) as e:

        @packtype.package()
        class TestPkg:
            A: Constant = 123
            B = 234

    assert str(e.value) == "TestPkg.B is not annotated"


def test_package_unsupported_annotation():
    with pytest.raises(BadFieldTypeError) as e:

        @packtype.package()
        class TestPkg:
            A: Constant = 123
            B: int = 234

    assert str(e.value) == "TestPkg.B is of an unsupported type int"


def test_package_unsupported_attribute():
    with pytest.raises(BadAttributeError) as e:

        @packtype.package(blah=True)
        class TestPkg:
            pass

    assert str(e.value) == "Unsupported attribute 'blah' for Package"


def test_package_foreign():
    @packtype.package()
    class InnerPkg:
        InnerType: Scalar[13]

    @InnerPkg.struct()
    class InnerStruct:
        abc: Scalar[21]

    @packtype.package()
    class OuterPkg:
        pass

    @OuterPkg.struct()
    class OuterStruct:
        ref_td: InnerPkg.InnerType
        ref_st: InnerStruct[2]

    assert OuterStruct
    assert InnerPkg._pt_foreign() == set()
    assert OuterPkg._pt_foreign() == {InnerPkg.InnerStruct, InnerPkg.InnerType}
