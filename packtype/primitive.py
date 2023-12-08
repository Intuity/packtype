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
    from typing import Self

from .base import Base, MetaBase


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


class Primitive(Base, metaclass=MetaPrimitive):
    _PT_WIDTH: int = -1
    _PT_SIGNED: bool = False

    def __init__(self, parent: Base | None = None, default: int | None = None) -> None:
        super().__init__(parent)
        if type(self)._PT_ALLOW_DEFAULT:
            self.__value = None if default is None else int(default)
        else:
            self.__value = 0

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
        return self.__value

    @value.setter
    def value(self, value: int) -> int:
        self._pt_set(value)

    def _pt_set(self, value: int) -> int:
        if value < 0 or (self._pt_width > 0 and value > self._pt_mask):
            raise PrimitiveValueError(
                f"Value {value} cannot be represented by {self._pt_width} bits"
            )
        self.__value = value
        self._pt_updated()

    def __int__(self) -> int:
        return self.__value

    # ==========================================================================
    # Operator overrides
    # ==========================================================================

    def __add__(self, other: int | Self) -> int:
        return int(self) + int(other)

    def __sub__(self, other: int | Self) -> int:
        return int(self) - int(other)

    def __mul__(self, other: int | Self) -> int:
        if isinstance(other, MetaBase):
            return int(self) * other
        else:
            return int(self) * int(other)

    def __truediv__(self, other: int | Self) -> int:
        return int(self) / int(other)

    def __floordiv__(self, other: int | Self) -> int:
        return int(self) // int(other)

    def __mod__(self, other: int | Self) -> int:
        return int(self) % int(other)

    def __divmod__(self, other: int | Self) -> int:
        return (int(self) // int(other), int(self) % int(other))

    def __pow__(self, other: int | Self) -> int:
        return int(self) ** int(other)

    def __lshift__(self, other: int | Self) -> int:
        return int(self) << int(other)

    def __rshift__(self, other: int | Self) -> int:
        return int(self) >> int(other)

    def __and__(self, other: int | Self) -> int:
        return int(self) & int(other)

    def __xor__(self, other: int | Self) -> int:
        return int(self) ^ int(other)

    def __or__(self, other: int | Self) -> int:
        return int(self) | int(other)

    def __radd__(self, other: int | Self) -> int:
        return int(other) + int(self)

    def __rsub__(self, other: int | Self) -> int:
        return int(other) - int(self)

    def __rmul__(self, other: int | Self) -> int:
        return int(other) * int(self)

    def __rtruediv__(self, other: int | Self) -> int:
        return int(other) / int(self)

    def __rfloordiv__(self, other: int | Self) -> int:
        return int(other) // int(self)

    def __rmod__(self, other: int | Self) -> int:
        return int(other) % int(self)

    def __rdivmod__(self, other: int | Self) -> int:
        return (int(other) // int(self), int(other) % int(self))

    def __rpow__(self, other: int | Self) -> int:
        return int(other) ** int(self)

    def __rlshift__(self, other: int | Self) -> int:
        return int(other) << int(self)

    def __rrshift__(self, other: int | Self) -> int:
        return int(other) >> int(self)

    def __rand__(self, other: int | Self) -> int:
        return int(other) & int(self)

    def __rxor__(self, other: int | Self) -> int:
        return int(other) ^ int(self)

    def __ror__(self, other: int | Self) -> int:
        return int(other) | int(self)

    def __iadd__(self, other: int | Self) -> int:
        return int(self) + int(other)

    def __isub__(self, other: int | Self) -> int:
        return int(self) - int(other)

    def __imul__(self, other: int | Self) -> int:
        return int(self) * int(other)

    def __itruediv__(self, other: int | Self) -> int:
        return int(self) / int(other)

    def __ifloordiv__(self, other: int | Self) -> int:
        return int(self) // int(other)

    def __imod__(self, other: int | Self) -> int:
        return int(self) % int(other)

    def __ipow__(self, other: int | Self) -> int:
        return int(self) ** int(other)

    def __ilshift__(self, other: int | Self) -> int:
        return int(self) << int(other)

    def __irshift__(self, other: int | Self) -> int:
        return int(self) >> int(other)

    def __iand__(self, other: int | Self) -> int:
        return int(self) & int(other)

    def __ixor__(self, other: int | Self) -> int:
        return int(self) ^ int(other)

    def __ior__(self, other: int | Self) -> int:
        return int(self) | int(other)

    def __neg__(self) -> int:
        return -1 * int(self)

    def __pos__(self) -> int:
        return abs(int(self))

    def __abs__(self) -> int:
        return abs(int(self))

    def __invert__(self) -> int:
        return ~int(self)

    def __lt__(self, other: int | Self) -> bool:
        return int(self) < int(other)

    def __le__(self, other: int | Self) -> bool:
        return int(self) <= int(other)

    def __eq__(self, other: int | Self) -> bool:
        return int(self) == int(other)

    def __ne__(self, other: int | Self) -> bool:
        return int(self) != int(other)

    def __gt__(self, other: int | Self) -> bool:
        return int(self) > int(other)

    def __ge__(self, other: int | Self) -> bool:
        return int(self) >= int(other)

    def __hash__(self) -> int:
        return id(self)
