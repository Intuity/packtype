# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from packtype import utils
from packtype.grammar.grammar import parse_string

from ..fixtures import reset_registry

assert reset_registry


def test_utils_enum_get_entries():
    PackageA = next(parse_string(  # noqa: N806
        """
        package PackageA {
            A: constant = 1
            B: constant = 2
            C: constant = A + B
        }
        """,
        keep_expression=True,
    ))
    assert utils.constant.get_expression(PackageA.C) is not None
    assert utils.constant.get_expression(PackageA.C).evaluate({"A": 3, "B": 4}.get) == 3 + 4
