# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from .primitive import NumericPrimitive


class Scalar(NumericPrimitive):
    _PT_WIDTH: int = 1
