# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype import Alias, Scalar
from packtype.grammar import UnknownEntityError, parse_string
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_alias():
    """Test parsing an alias definition within a package"""
    pkg = parse_string(
        """
        package the_package {
            // Original scalar
            original: scalar[8]
            // Alias to the original scalar
            alias: original
        }
        """
    )
    assert len(pkg._PT_FIELDS) == 2
    # original
    assert issubclass(pkg.original, Scalar)
    assert get_width(pkg.original) == 8
    # alias
    assert issubclass(pkg.alias, Alias)
    assert get_width(pkg.alias) == 8


def test_parse_alias_bad_reference():
    """Test parsing an alias definition with an invalid reference."""
    with pytest.raises(
        UnknownEntityError,
        match="Failed to resolve 'non_existent' to a known constant or type",
    ):
        parse_string(
            """
            package the_package {
                alias: non_existent
            }
            """
        )
