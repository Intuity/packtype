# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype import Constant
from packtype.grammar import ParseError, UnknownConstantError, parse_string
from packtype.utils import width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_constant():
    """Test parsing a constant definition within a package"""
    pkg = parse_string(
        """
        package the_package {
            // Unsized declaration
            A: constant = 42
            // Sized declaration
            B: constant[8] = 0x42
            // Declarations are case insensitive
            C: CONSTANT[12] = 0x123
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 3
    # A
    assert isinstance(pkg.A, Constant)
    assert pkg.A.value == 42
    assert width(pkg.A) == -1
    # B
    assert isinstance(pkg.B, Constant)
    assert pkg.B.value == 0x42
    assert width(pkg.B) == 8
    # C
    assert isinstance(pkg.C, Constant)
    assert pkg.C.value == 0x123
    assert width(pkg.C) == 12


def test_parse_constant_no_value():
    """Test parsing a constant definition without a value."""
    with pytest.raises(ParseError, match="Failed to parse input"):
        parse_string(
            """
            package the_package {
                A: CONSTANT[12]
            }
            """
        )


def test_parse_constant_bad_reference():
    """Test an expression that refers to a constant that is not defined."""
    with pytest.raises(UnknownConstantError, match="Failed to resolve 'NON_EXISTENT' to a known constant"):
        parse_string(
            """
            package the_package {
                A: CONSTANT[12] = NON_EXISTENT + 1
            }
            """
        )



def test_parse_constant_expression():
    """Check that a complex expression is evaluated correctly"""
    pkg = parse_string(
        """
        package the_package {
            A: Constant = 32
            B: Constant = 9
            C: Constant = 2
            D: Constant = -4
            E: Constant = 43
            F: Constant = ((A * B) ** C) / D + E
        }
        """
    )
    assert int(pkg.F) == (32 * 9) ** 2 // -4 + 43
