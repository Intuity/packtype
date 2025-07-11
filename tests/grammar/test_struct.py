# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.grammar import ParseError, UnknownEntityError, parse_string
from packtype.types.assembly import Packing, WidthError
from packtype.types.struct import Struct
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_struct():
    """Test parsing a struct definition."""
    pkg = parse_string(
        """
        package the_package {
            // Implicit width, implicitly packed from LSB
            struct a {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
            // Implicit width, explicitly packed from LSB
            struct lsb b {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
            // Implicit width, explicitly packed from MSB
            struct msb c {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
            // Implicit width, explicitly packed from LSB (alternative syntax)
            struct from_lsb e {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
            // Implicit width, explicitly packed from MSB (alternative syntax)
            struct from_msb f {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
            // Explicit width, implicitly packed from LSB
            struct [60] g {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
            // Explicit width, explicitly packed from LSB
            struct lsb [60] h {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
            // Explicit width, explicitly packed from MSB
            struct msb [60] i {
                a: scalar[8]
                b: scalar[16]
                c: scalar[32]
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 8
    # a
    assert issubclass(pkg.a, Struct)
    assert get_width(pkg.a) == 56
    assert pkg.a._PT_PACKING is Packing.FROM_LSB
    assert pkg.a._PT_RANGES == {"a": (0, 7), "b": (8, 23), "c": (24, 55)}
    # b
    assert issubclass(pkg.b, Struct)
    assert get_width(pkg.b) == 56
    assert pkg.b._PT_PACKING is Packing.FROM_LSB
    assert pkg.b._PT_RANGES == {"a": (0, 7), "b": (8, 23), "c": (24, 55)}
    # c
    assert issubclass(pkg.c, Struct)
    assert get_width(pkg.c) == 56
    assert pkg.c._PT_PACKING is Packing.FROM_MSB
    assert pkg.c._PT_RANGES == {"a": (48, 55), "b": (32, 47), "c": (0, 31)}
    # e
    assert issubclass(pkg.e, Struct)
    assert get_width(pkg.e) == 56
    assert pkg.e._PT_PACKING is Packing.FROM_LSB
    assert pkg.e._PT_RANGES == {"a": (0, 7), "b": (8, 23), "c": (24, 55)}
    # f
    assert issubclass(pkg.f, Struct)
    assert get_width(pkg.f) == 56
    assert pkg.f._PT_PACKING is Packing.FROM_MSB
    assert pkg.f._PT_RANGES == {"a": (48, 55), "b": (32, 47), "c": (0, 31)}
    # g
    assert issubclass(pkg.g, Struct)
    assert get_width(pkg.g) == 60
    assert pkg.g._PT_PACKING is Packing.FROM_LSB
    assert pkg.g._PT_RANGES == {"a": (0, 7), "b": (8, 23), "c": (24, 55), "_padding": (56, 59)}
    # h
    assert issubclass(pkg.h, Struct)
    assert get_width(pkg.h) == 60
    assert pkg.h._PT_PACKING is Packing.FROM_LSB
    assert pkg.h._PT_RANGES == {"a": (0, 7), "b": (8, 23), "c": (24, 55), "_padding": (56, 59)}
    # i
    assert issubclass(pkg.i, Struct)
    assert get_width(pkg.i) == 60
    assert pkg.i._PT_PACKING is Packing.FROM_MSB
    assert pkg.i._PT_RANGES == {"a": (52, 59), "b": (36, 51), "c": (4, 35), "_padding": (0, 3)}


def test_parse_struct_description():
    """Check that a struct can have a description"""
    pkg = parse_string(
        """
        package the_package {
            struct simple_struct {
                "This is a simple struct"
                a: scalar[2]
                b: scalar[3]
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 1
    assert issubclass(pkg.simple_struct, Struct)
    assert get_width(pkg.simple_struct) == 5
    assert pkg.simple_struct.__doc__ == "This is a simple struct"


def test_parse_struct_reference():
    """Check that a struct can reference other known types"""
    pkg = parse_string(
        """
        package the_package {
            single_bit: scalar
            multi_bit: scalar[8]
            struct simple_struct {
                a: scalar[2]
                b: scalar[3]
            }
            struct compound_struct {
                a: simple_struct
                b: single_bit
                c: multi_bit
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 4
    assert issubclass(pkg.compound_struct, Struct)
    assert get_width(pkg.compound_struct) == 14
    inst = pkg.compound_struct()
    assert get_width(inst.a.a) == 2
    assert get_width(inst.a.b) == 3
    assert get_width(inst.b) == 1
    assert get_width(inst.c) == 8


def test_parse_struct_oversized():
    """Check an error is raised if the field width exceeds the struct width"""
    with pytest.raises(
        WidthError,
        match="Fields of oversized_struct total 56 bits which does not fit "
        "within the specified width of 8 bits",
    ):
        parse_string(
            """
            package the_package {
                struct [8] oversized_struct {
                    a: scalar[8]
                    b: scalar[16]
                    c: scalar[32]
                }
            }
            """
        )


def test_parse_struct_bad_decl():
    """Check that an error is raised if packing order and width are mixed up"""
    with pytest.raises(ParseError, match="Failed to parse"):
        parse_string(
            """
            package the_package {
                struct [60] msb bad_struct {
                    a: scalar[8]
                    b: scalar[16]
                    c: scalar[32]
                }
            }
            """
        )


def test_parse_struct_bad_field_ref():
    """Check that an error is raised if an unkown type is referenced in a struct"""
    with pytest.raises(
        UnknownEntityError, match="Failed to resolve 'non_existent' to a known constant or type"
    ):
        parse_string(
            """
            package the_package {
                struct bad_struct {
                    a: non_existent
                }
            }
            """
        )
