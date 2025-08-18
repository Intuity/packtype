# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from ..common.expression import Expression
from .primitive import NumericPrimitive


class Constant(NumericPrimitive):
    _PT_EXPRESSION: Expression | None = None

    def __str__(self) -> str:
        as_str = "<Constant"
        if self._pt_width is not None and self._pt_width > 0:
            as_str += f"[{self._pt_width}]"
        if self._pt_signed:
            as_str += " signed"
        return as_str + f" value={self.value}>"

    def __repr__(self) -> str:
        return str(self)
