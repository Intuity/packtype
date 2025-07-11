# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype import Scalar
from packtype.grammar import ParseError, parse_string
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_scalar():
    """Test parsing a scalar definition within a package"""
    pkg = parse_string(
        """
        package the_package {
            single_bit: scalar
                "Single bit scalar"
            multi_bit_8: scalar[8]
                "Multi-bit scalar"
            multi_bit_12: SCALAR[12]
                "Declarations are case insensitive"
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 3
    # single_bit
    assert issubclass(pkg.single_bit, Scalar)
    assert get_width(pkg.single_bit) == 1
    assert pkg.single_bit.__doc__ == "Single bit scalar"
    # multi_bit_8
    assert issubclass(pkg.multi_bit_8, Scalar)
    assert get_width(pkg.multi_bit_8) == 8
    assert pkg.multi_bit_8.__doc__ == "Multi-bit scalar"
    # multi_bit_12
    assert issubclass(pkg.multi_bit_12, Scalar)
    assert get_width(pkg.multi_bit_12) == 12
    assert pkg.multi_bit_12.__doc__ == "Declarations are case insensitive"


def test_parse_scalar_bad_assign():
    """Test parsing a scalar definition with an invalid assignment."""
    with pytest.raises(ParseError, match="Failed to parse input"):
        parse_string(
            """
            package the_package {
                A: scalar[8] = 42
            }
            """
        )
