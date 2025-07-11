# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype import Constant
from packtype.grammar import ParseError, UnknownEntityError, parse_string
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_constant():
    """Test parsing a constant definition within a package"""
    pkg = parse_string(
        """
        package the_package {
            A: constant = 42
                "Unsized declaration"
            B: constant[8] = 0x42
                "Sized declaration"
            C: CONSTANT[12] = 0x123
                "Declarations are case insensitive"
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 3
    # A
    assert isinstance(pkg.A, Constant)
    assert pkg.A.value == 42
    assert get_width(pkg.A) == -1
    assert pkg.A.__doc__ == "Unsized declaration"
    # B
    assert isinstance(pkg.B, Constant)
    assert pkg.B.value == 0x42
    assert get_width(pkg.B) == 8
    assert pkg.B.__doc__ == "Sized declaration"
    # C
    assert isinstance(pkg.C, Constant)
    assert pkg.C.value == 0x123
    assert get_width(pkg.C) == 12
    assert pkg.C.__doc__ == "Declarations are case insensitive"


def test_parse_constant_override():
    """Test parsing a constant definition within a package"""
    # Parse without overrides
    pkg = parse_string(
        """
        package the_package {
            A: constant = 42
            B: constant = 39
            C: constant = A + B
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 3
    # A
    assert isinstance(pkg.A, Constant)
    assert pkg.A.value == 42
    # B
    assert isinstance(pkg.B, Constant)
    assert pkg.B.value == 39
    # C
    assert isinstance(pkg.C, Constant)
    assert pkg.C.value == 42 + 39
    # Parse with overrides
    pkg = parse_string(
        """
        package the_package {
            A: constant = 42
            B: constant = 39
            C: constant = A + B
        }
        """,
        constant_overrides={
            "A": 123,
            "B": 456,
        },
    )
    assert len(pkg._PT_FIELDS) == 3
    # A
    assert isinstance(pkg.A, Constant)
    assert pkg.A.value == 123
    # B
    assert isinstance(pkg.B, Constant)
    assert pkg.B.value == 456
    # C
    assert isinstance(pkg.C, Constant)
    assert pkg.C.value == 123 + 456


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
    with pytest.raises(
        UnknownEntityError, match="Failed to resolve 'NON_EXISTENT' to a known constant"
    ):
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
