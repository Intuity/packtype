# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from ..common.expression import Expression
from ..types.constant import Constant


def get_expression(constant: Constant) -> Expression | None:
    """Get the expression associated with a constant."""
    return constant._PT_EXPRESSION
