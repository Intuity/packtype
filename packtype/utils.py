# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math
from .base import Base


def clog2(x: int) -> int:
    """Calculate the ceiling of the base-2 logarithm of x."""
    assert x > 0, "Input must be a positive integer."
    return math.ceil(math.log2(x))


def width(ptype: type[Base]) -> int:
    """Get the width of a Packtype definition"""
    if isinstance(ptype, Base):
        return ptype._pt_width
    elif issubclass(ptype, Base):
        return ptype._PT_WIDTH
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")
