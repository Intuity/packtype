# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.grammar import ParseError, parse_string
from packtype.types.enum import Enum, EnumError, EnumMode
from packtype.types.wrap import BadAttributeError
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_enum():
    """Test parsing an enum definition."""
    pkg = parse_string(
        """
        package the_package {
            // Default behaviours (implicit width, indexed)
            enum a {
                A
                B
                C
                D
            }
            // Implicit width, explicitly indexed
            enum indexed b {
                A
                B
                C
                D
            }
            // Implicit width, explicitly onehot
            enum onehot c {
                A
                B
                C
                D
            }
            // Implicit width, implicitly Gray coded
            enum gray d {
                A
                B
                C
                D
            }
            // Explicit width, implicitly indexed
            enum [4] e {
                A
                B
                C
                D
            }
            // Explicit width, explicitly onehot
            enum onehot [8] f {
                A
                B
                C
                D
            }
            // Explicit width, implicitly Gray coded
            enum gray [2] g {
                A
                B
                C
                D
            }
            // Explicit assignments
            enum [8] h {
                A = 0x12
                B = 0x34
                C = 0x56
                D = 0x78
            }
            // Mixed implicit and explicit assignments
            enum [8] i {
                A = 0x12
                B
                C = 0x56
                D
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 9
    # a
    assert issubclass(pkg.a, Enum)
    assert get_width(pkg.a) == 2
    assert pkg.a._PT_MODE is EnumMode.INDEXED
    assert [pkg.a.A, pkg.a.B, pkg.a.C, pkg.a.D] == [0, 1, 2, 3]
    # b
    assert issubclass(pkg.b, Enum)
    assert get_width(pkg.b) == 2
    assert pkg.b._PT_MODE is EnumMode.INDEXED
    assert [pkg.b.A, pkg.b.B, pkg.b.C, pkg.b.D] == [0, 1, 2, 3]
    # c
    assert issubclass(pkg.c, Enum)
    assert get_width(pkg.c) == 4
    assert pkg.c._PT_MODE is EnumMode.ONE_HOT
    assert [pkg.c.A, pkg.c.B, pkg.c.C, pkg.c.D] == [1, 2, 4, 8]
    # d
    assert issubclass(pkg.d, Enum)
    assert get_width(pkg.d) == 2
    assert pkg.d._PT_MODE is EnumMode.GRAY
    assert [pkg.d().A, pkg.d().B, pkg.d().C, pkg.d().D] == [0, 1, 3, 2]
    # e
    assert issubclass(pkg.e, Enum)
    assert get_width(pkg.e) == 4
    assert pkg.e._PT_MODE is EnumMode.INDEXED
    assert [pkg.e.A, pkg.e.B, pkg.e.C, pkg.e.D] == [0, 1, 2, 3]
    # f
    assert issubclass(pkg.f, Enum)
    assert get_width(pkg.f) == 8
    assert pkg.f._PT_MODE is EnumMode.ONE_HOT
    assert [pkg.f.A, pkg.f.B, pkg.f.C, pkg.f.D] == [1, 2, 4, 8]
    # g
    assert issubclass(pkg.g, Enum)
    assert get_width(pkg.g) == 2
    assert pkg.g._PT_MODE is EnumMode.GRAY
    assert [pkg.g().A, pkg.g().B, pkg.g().C, pkg.g().D] == [0, 1, 3, 2]
    # h
    assert issubclass(pkg.h, Enum)
    assert get_width(pkg.h) == 8
    assert pkg.h._PT_MODE is EnumMode.INDEXED
    assert [pkg.h().A, pkg.h().B, pkg.h().C, pkg.h().D] == [0x12, 0x34, 0x56, 0x78]
    # i
    assert issubclass(pkg.i, Enum)
    assert get_width(pkg.i) == 8
    assert pkg.i._PT_MODE is EnumMode.INDEXED
    assert [pkg.i().A, pkg.i().B, pkg.i().C, pkg.i().D] == [0x12, 0x13, 0x56, 0x57]


def test_parse_enum_description():
    """Test parsing an enum definition with a description."""
    pkg = parse_string(
        """
        package the_package {
            // Default behaviours (implicit width, indexed)
            enum a {
                "This is an enum"
                A
                B
                C
                D
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 1
    assert issubclass(pkg.a, Enum)
    assert get_width(pkg.a) == 2
    assert pkg.a._PT_MODE is EnumMode.INDEXED
    assert pkg.a.__doc__ == "This is an enum"
    assert int(pkg.a.A) == 0
    assert int(pkg.a.B) == 1
    assert int(pkg.a.C) == 2
    assert int(pkg.a.D) == 3


def test_parse_enum_modifiers():
    """Test parsing an enum definition with modifiers."""
    pkg = parse_string(
        """
        package the_package {
            // Default behaviours (implicit width, indexed)
            enum a {
                "This is an enum"
                @prefix=ABC
                A
                B
                C
                D
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 1
    assert issubclass(pkg.a, Enum)
    assert get_width(pkg.a) == 2
    assert pkg.a._PT_MODE is EnumMode.INDEXED
    assert pkg.a.__doc__ == "This is an enum"
    assert pkg.a._PT_ATTRIBUTES["prefix"] == "ABC"
    assert int(pkg.a.A) == 0
    assert int(pkg.a.B) == 1
    assert int(pkg.a.C) == 2
    assert int(pkg.a.D) == 3


def test_parse_enum_descriptions():
    """Test parsing an enum definition with descriptions."""
    pkg = parse_string(
        """
        package the_package {
            // Default behaviours (implicit width, indexed)
            enum a {
                "This is an enum"
                A
                    "This is A"
                B : constant
                    "This is B"
                C : constant = 2
                    "This is C"
                D = 3
                    "This is D"
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 1
    assert issubclass(pkg.a, Enum)
    assert get_width(pkg.a) == 2
    assert pkg.a._PT_MODE is EnumMode.INDEXED
    assert pkg.a.__doc__ == "This is an enum"
    assert int(pkg.a.A) == 0
    assert pkg.a.A.__doc__ == "This is A"
    assert int(pkg.a.B) == 1
    assert pkg.a.B.__doc__ == "This is B"
    assert int(pkg.a.C) == 2
    assert pkg.a.C.__doc__ == "This is C"
    assert int(pkg.a.D) == 3
    assert pkg.a.D.__doc__ == "This is D"


def test_parse_enum_bad_field():
    """Test parsing an enum definition with a bad field."""
    with pytest.raises(ParseError, match="Failed to parse input"):
        parse_string(
            """
            package the_package {
                enum a {
                    A : scalar[4]
                }
            }
            """
        )


def test_parse_enum_bad_width():
    """Test parsing an enum where values exceed the width."""
    with pytest.raises(
        EnumError, match="Enum entry E has value 4 that cannot be encoded in a bit width of 2"
    ):
        parse_string(
            """
            package the_package {
                enum [2] a {
                    A
                    B
                    C
                    D
                    E
                }
            }
            """
        )


def test_parse_enum_bad_modifier():
    """Test parsing an enum where an unrecognised modifier is used."""
    with pytest.raises(BadAttributeError, match="Unsupported attribute 'blargh' for Enum"):
        parse_string(
            """
            package the_package {
                enum [2] a {
                    @blargh=123
                    A
                    B
                    C
                    D
                }
            }
            """
        )
