# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.grammar import ParseError, parse_string
from packtype.types.scalar import ScalarType
from packtype.utils import get_width, pack, unpack
from packtype.utils.basic import copy

from ..fixtures import reset_registry

assert reset_registry


def test_parse_scalar():
    """Test parsing a scalar definition within a package"""
    pkg = next(
        parse_string(
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
    )
    assert len(pkg._PT_FIELDS) == 3
    # single_bit
    assert issubclass(pkg.single_bit, ScalarType)
    assert get_width(pkg.single_bit) == 1
    assert pkg.single_bit.__doc__ == "Single bit scalar"
    # multi_bit_8
    assert issubclass(pkg.multi_bit_8, ScalarType)
    assert get_width(pkg.multi_bit_8) == 8
    assert pkg.multi_bit_8.__doc__ == "Multi-bit scalar"
    # multi_bit_12
    assert issubclass(pkg.multi_bit_12, ScalarType)
    assert get_width(pkg.multi_bit_12) == 12
    assert pkg.multi_bit_12.__doc__ == "Declarations are case insensitive"


def test_parse_scalar_bad_assign():
    """Test parsing a scalar definition with an invalid assignment."""
    with pytest.raises(ParseError, match="Failed to parse input"):
        next(
            parse_string(
                """
            package the_package {
                A: scalar[8] = 42
            }
            """
            )
        )


def test_parse_scalar_copy():
    """Test copying a scalar instance."""
    pkg = next(
        parse_string(
            """
        package the_package {
            my_scalar: scalar[8]
        }
        """
        )
    )
    inst = unpack(pkg.my_scalar, 0x7B)
    inst_copy = copy(inst)

    assert isinstance(inst_copy, ScalarType)
    assert inst_copy == inst
    assert inst_copy is not inst
    assert pack(inst_copy) == pack(inst)
    assert inst_copy._pt_bv.value == inst._pt_bv.value
    assert inst_copy._pt_bv is not inst._pt_bv
