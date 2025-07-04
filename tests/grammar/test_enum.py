# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype import Constant
from packtype.enum import Enum, EnumMode
from packtype.grammar import ParseError, parse_string
from packtype.utils import width

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
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 7
    # a
    assert issubclass(pkg.a, Enum)
    assert width(pkg.a) == 2
    assert pkg.a._PT_MODE is EnumMode.INDEXED
    assert [pkg.a.A, pkg.a.B, pkg.a.C, pkg.a.D] == [0, 1, 2, 3]
    # b
    assert issubclass(pkg.b, Enum)
    assert width(pkg.b) == 2
    assert pkg.b._PT_MODE is EnumMode.INDEXED
    assert [pkg.b.A, pkg.b.B, pkg.b.C, pkg.b.D] == [0, 1, 2, 3]
    # c
    assert issubclass(pkg.c, Enum)
    assert width(pkg.c) == 4
    assert pkg.c._PT_MODE is EnumMode.ONE_HOT
    assert [pkg.c.A, pkg.c.B, pkg.c.C, pkg.c.D] == [1, 2, 4, 8]
    # d
    assert issubclass(pkg.d, Enum)
    assert width(pkg.d) == 2
    assert pkg.d._PT_MODE is EnumMode.GRAY
    assert [pkg.d().A, pkg.d().B, pkg.d().C, pkg.d().D] == [0, 1, 3, 2]
    # e
    assert issubclass(pkg.e, Enum)
    assert width(pkg.e) == 4
    assert pkg.e._PT_MODE is EnumMode.INDEXED
    assert [pkg.e.A, pkg.e.B, pkg.e.C, pkg.e.D] == [0, 1, 2, 3]
    # f
    assert issubclass(pkg.f, Enum)
    assert width(pkg.f) == 8
    assert pkg.f._PT_MODE is EnumMode.ONE_HOT
    assert [pkg.f.A, pkg.f.B, pkg.f.C, pkg.f.D] == [1, 2, 4, 8]
    # g
    assert issubclass(pkg.g, Enum)
    assert width(pkg.g) == 2
    assert pkg.g._PT_MODE is EnumMode.GRAY
    assert [pkg.g().A, pkg.g().B, pkg.g().C, pkg.g().D] == [0, 1, 3, 2]
