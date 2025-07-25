# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from ..common.expression import Expression
from .primitive import NumericPrimitive


class Constant(NumericPrimitive):
    _PT_EXPRESSION: Expression | None = None
