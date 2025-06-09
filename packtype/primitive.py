# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections import defaultdict
from typing import Any

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self  # noqa: UP035

from .base import Base, MetaBase
from .bitvector import BitVector, BitVectorWindow
from .numeric import Numeric


class PrimitiveValueError(Exception):
    pass


class MetaPrimitive(MetaBase):
    UNIQUE_ID: dict[tuple[int, bool], int] = defaultdict(lambda: 0)

    def __getitem__(self, key: int | tuple[int, bool]):
        segments, kwargs = self._pt_meta_key(key)
        return MetaPrimitive.get_variant(self, segments, kwargs)

    @staticmethod
    def get_variant(prim: Self, segments: tuple[str], kwargs: dict[str, Any]):
        # NOTE: Don't share primitives between creations as this prevents the
        #       parent being distinctly tracked (a problem when they are used as
        #       typedefs on a package)
        uid = MetaPrimitive.UNIQUE_ID[segments]
        MetaPrimitive.UNIQUE_ID[segments] += 1
        return type(
            prim.__name__ + "_" + "_".join(str(x) for x in segments) + f"_{uid}",
            (prim,),
            kwargs,
        )


class NumericPrimitive(Base, Numeric, metaclass=MetaPrimitive):
    _PT_WIDTH: int = -1
    _PT_SIGNED: bool = False

    def __init__(
        self,
        default: int | None = None,
        _pt_bv: BitVector | BitVectorWindow | None = None,
    ) -> None:
        super().__init__(_pt_bv=_pt_bv, default=default)

    @classmethod
    def _pt_meta_key(
        cls, key: int | tuple[int, bool]
    ) -> tuple[tuple[str], dict[str, Any]]:
        if isinstance(key, int) or hasattr(key, "__int__"):
            key = int(key)
            return ((str(key),), {"_PT_WIDTH": key})
        elif (
            isinstance(key, tuple)
            and (isinstance(key[0], int) or hasattr(key[0], "__int__"))
            and (isinstance(key[1], bool) or hasattr(key[1], "__bool__"))
        ):
            width, signed = int(key[0]), bool(key[1])
            return ((str(key),), {"_PT_WIDTH": width, "_PT_SIGNED": signed})
        else:
            raise Exception(f"Unsupported NumericPrimitive key: {key}")

    @property
    def _pt_width(self) -> int:
        return type(self)._PT_WIDTH

    @property
    def _pt_signed(self) -> int:
        return type(self)._PT_SIGNED

    @property
    def _pt_mask(self) -> int:
        return (1 << type(self)._PT_WIDTH) - 1

    @property
    def value(self) -> int:
        return int(self._pt_bv)

    @value.setter
    def value(self, value: int) -> int:
        self._pt_set(value)

    def _pt_set(self, value: int) -> int:
        value = int(value)
        if value < 0 or (self._pt_width > 0 and value > self._pt_mask):
            raise PrimitiveValueError(
                f"Value {value} cannot be represented by {self._pt_width} bits"
            )
        self._pt_bv.set(value)

    def __int__(self) -> int:
        return int(self._pt_bv)
