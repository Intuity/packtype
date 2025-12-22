# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.grammar import ParseError, parse_string
from packtype.types.requirement import Priority

from ..fixtures import reset_registry

assert reset_registry


def test_parse_req():
    """Test that requirement tag attributes are correctly set."""
    pkg = next(
        parse_string(
            """
        package the_package {
            requirement my_feature : P1 "This feature is high priority"
        }
        """
        )
    )
    assert "my_feature" in pkg._PT_REQUIREMENTS
    assert pkg._PT_REQUIREMENTS["my_feature"]._PT_ATTRIBUTES["priority"] == Priority.P1
    assert pkg.my_feature._PT_ATTRIBUTES["priority"] == Priority.P1


def test_parse_erroneous_priority():
    """Test that priority typo missing index is caught."""
    with pytest.raises(ParseError, match="Failed to parse input on line 3"):
        next(
            parse_string(
                """
                package the_package {
                requirement my_feature : P "This feature is high priority"
                }
                """
            )
        )


def test_parse_priority_typo():
    """Check that a typo for unsupported Priority is caught"""
    with pytest.raises(KeyError, match="P5"):
        next(
            parse_string(
                """
                package the_package {
                requirement my_feature : P5 "This feature's priority is wrong!"
                }
                """
            )
        )
