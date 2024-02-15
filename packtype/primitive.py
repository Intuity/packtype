# Copyright 2023, Peter Birch, mailto:peter@intuity.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict

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
        if isinstance(key, tuple):
            width, signed, *_ = key
        else:
            width = key
            signed = False
        return MetaPrimitive.get_variant(self, int(width), signed)

    @staticmethod
    def get_variant(prim: Self, width: int, signed: bool):
        # NOTE: Don't share primitives between creations as this prevents the
        #       parent being distinctly tracked (a problem when they are used as
        #       typedefs on a package)
        uid = MetaPrimitive.UNIQUE_ID[width, signed]
        MetaPrimitive.UNIQUE_ID[width, signed] += 1
        return type(
            prim.__name__ + f"_{width}_{['U','S'][signed]}{uid}",
            (prim,),
            {"_PT_WIDTH": width, "_PT_SIGNED": signed},
        )


class Primitive(Base, Numeric, metaclass=MetaPrimitive):
    _PT_WIDTH: int = -1
    _PT_SIGNED: bool = False

    def __init__(self,
                 default: int | None = None,
                 _pt_bv: BitVector | BitVectorWindow | None = None) -> None:
        super().__init__(_pt_bv=_pt_bv)
        if type(self)._PT_ALLOW_DEFAULT:
            self._pt_bv.set(0 if default is None else int(default))

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
