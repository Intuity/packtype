# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math

import packtype
from packtype import Scalar, utils

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
