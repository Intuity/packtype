# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.grammar import UnknownEntityError, parse_string
from packtype.types.union import Union, UnionError
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_union():
    """Parse simple union definitions."""
    pkg = parse_string(
        """
        package the_package {
            union with_descr {
                "This is a simple union"
                a: scalar[2]
                b: scalar[2]
            }
            union without_descr {
                a: scalar[2]
                b: scalar[2]
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 2
    # with_descr
    assert issubclass(pkg.with_descr, Union)
    assert get_width(pkg.with_descr) == 2
    assert pkg.with_descr.__doc__ == "This is a simple union"
    # without_descr
    assert issubclass(pkg.without_descr, Union)
    assert get_width(pkg.without_descr) == 2
    assert pkg.without_descr.__doc__ is None


def test_parse_union_complex():
    """Check that unions can refer to other types."""
    pkg = parse_string(
        """
        package the_package {
            a_scalar: scalar[8]

            struct [8] a_struct {
                a: scalar[2]
            }

            union a_union {
                a: scalar[8]
                b: scalar[8]
            }

            union complex {
                a_scalar: a_scalar
                a_struct: a_struct
                a_union: a_union
            }
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 4
    assert issubclass(pkg.complex, Union)
    assert get_width(pkg.complex) == 8
    inst = pkg.complex()
    assert isinstance(inst.a_scalar, pkg.a_scalar)
    assert isinstance(inst.a_struct, pkg.a_struct)
    assert isinstance(inst.a_union, pkg.a_union)


def test_parse_union_mismatched_sizes():
    """Check that an error is raised if union members have mismatched sizes."""
    with pytest.raises(
        UnionError,
        match="Union member b has a width of 4 that differs from the expected width of 2",
    ):
        parse_string(
            """
            package the_package {
                union mismatched {
                    a: scalar[2]
                    b: scalar[4]
                }
            }
            """
        )


def test_parse_union_bad_field_ref():
    """Check that an error is raised if an unknown type is referenced in a union"""
    with pytest.raises(
        UnknownEntityError, match="Failed to resolve 'non_existent' to a known constant or type"
    ):
        parse_string(
            """
            package the_package {
                union bad_union {
                    a: non_existent
                }
            }
            """
        )
