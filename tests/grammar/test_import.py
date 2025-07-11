# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype import Constant, Scalar
from packtype.grammar import ParseError, parse_string
from packtype.types.struct import Struct
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_import():
    """Test parsing an import statement"""
    # First package
    pkg_a = parse_string(
        """
        package pkg_a {
            A: constant = 42
            a_sclr: scalar[A]
        }
        """
    )
    # Second package with import
    pkg_b = parse_string(
        """
        package another_package {
            import pkg_a::A
            import pkg_a::a_sclr
            B: constant = A + 1
            struct test_struct {
                a: a_sclr
                b: scalar[B]
            }
        }
        """,
        namespaces={"pkg_a": pkg_a},
    )

    # Package A
    assert len(pkg_a._PT_FIELDS) == 2

    assert isinstance(pkg_a.A, Constant)
    assert pkg_a.A.value == 42
    assert get_width(pkg_a.A) == -1

    assert issubclass(pkg_a.a_sclr, Scalar)
    assert get_width(pkg_a.a_sclr) == 42

    # Package B
    assert len(pkg_b._PT_FIELDS) == 2

    assert isinstance(pkg_b.B, Constant)
    assert pkg_b.B.value == 42 + 1
    assert get_width(pkg_b.B) == -1

    assert pkg_b.test_struct._PT_BASE is Struct
    assert get_width(pkg_b.test_struct) == 42 + (42 + 1)


def test_parse_import_bad():
    """Test parsing an import statement with a bad import statement"""
    with pytest.raises(ParseError, match="Failed to parse input"):
        parse_string(
            """
            package the_package {
                import pkg_a::
            }
            """
        )


def test_parse_import_unknown():
    """Test parsing an import statement with an unknwown package"""
    with pytest.raises(ImportError, match="Unknown package 'pkg_a'"):
        parse_string(
            """
            package the_package {
                import pkg_a::B
            }
            """
        )
    with pytest.raises(ImportError, match="'B' not declared in package 'pkg_a'"):
        pkg_a = parse_string(r"package pkg_a {}")
        parse_string(
            """
            package the_package {
                import pkg_a::B
            }
            """,
            namespaces={"pkg_a": pkg_a},
        )
