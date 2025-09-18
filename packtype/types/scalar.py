# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#


from .base import Base
from .primitive import NumericPrimitive, NumericType


class ScalarType(NumericType):
    _PT_WIDTH: int = 1

    @classmethod
    def _pt_name(cls) -> str:
        if cls._PT_ATTACHED_TO is not None:
            return cls._PT_ATTACHED_TO._pt_lookup(cls)
        else:
            return f"{['Unsigned', 'Signed'][cls._PT_SIGNED]} Scalar[{cls._PT_WIDTH}]"

    def __str__(self) -> str:
        return f"{type(self)._pt_name()}: 0x{int(self):0{self._PT_WIDTH // 4}X}"

    def __repr__(self):
        return str(self)


class Scalar(NumericPrimitive):
    _PT_META_USE_TYPE: type[Base] = ScalarType
