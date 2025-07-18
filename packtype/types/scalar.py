# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from .primitive import NumericPrimitive


class Scalar(NumericPrimitive):
    _PT_WIDTH: int = 1

    @classmethod
    def _pt_name(cls) -> str:
        if cls._PT_ATTACHED_TO is not None:
            return cls._PT_ATTACHED_TO._pt_lookup(cls)
        else:
            return NumericPrimitive._pt_name(cls)
