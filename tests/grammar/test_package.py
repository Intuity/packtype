# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.grammar import ParseError, parse_string

from ..fixtures import reset_registry

assert reset_registry


def test_parse_package():
    """Test parsing a package definition."""
    pkg = parse_string(
        """
        package the_package {
            "This describes the package"
        }
        """
    )
    assert pkg.__name__ == "the_package"
    assert pkg._pt_name() == "the_package"
    assert pkg.__doc__ == "This describes the package"
    assert len(pkg._PT_FIELDS) == 0


def test_parse_package_unclosed():
    """Test parsing a package definition that is not closed."""
    with pytest.raises(ParseError, match="Failed to parse input"):
        parse_string(
            """
            package the_package {
                "This describes the package"
            """
        )
