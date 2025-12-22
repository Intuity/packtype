# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#


try:
    from typing import Self
except ImportError:
    from typing_extensions import Self  # noqa: UP035


class Numeric:
    def __int__(self) -> int:
        raise NotImplementedError("Subclass must implement __int__")

    # ==========================================================================
    # Operator overrides
    # ==========================================================================

    def __add__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) + other

    def __sub__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) - other

    def __mul__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) * other

    def __truediv__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) / other

    def __floordiv__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) // other

    def __mod__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) % other

    def __divmod__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return (int(self) // other, int(self) % other)

    def __pow__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) ** other

    def __lshift__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) << other

    def __rshift__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) >> other

    def __and__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) & other

    def __xor__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) ^ other

    def __or__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) | other

    def __radd__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other + int(self)

    def __rsub__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other - int(self)

    def __rmul__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other * int(self)

    def __rtruediv__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other / int(self)

    def __rfloordiv__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other // int(self)

    def __rmod__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other % int(self)

    def __rdivmod__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return (other // int(self), other % int(self))

    def __rpow__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other ** int(self)

    def __rlshift__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other << int(self)

    def __rrshift__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other >> int(self)

    def __rand__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other & int(self)

    def __rxor__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other ^ int(self)

    def __ror__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return other | int(self)

    def __iadd__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) + other

    def __isub__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) - other

    def __imul__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) * other

    def __itruediv__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) / other

    def __ifloordiv__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) // other

    def __imod__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) % other

    def __ipow__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) ** other

    def __ilshift__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) << other

    def __irshift__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) >> other

    def __iand__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) & other

    def __ixor__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) ^ other

    def __ior__(self, other) -> int:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) | other

    def __neg__(self) -> int:
        return -1 * int(self)

    def __pos__(self) -> int:
        return abs(int(self))

    def __abs__(self) -> int:
        return abs(int(self))

    def __index__(self) -> int:
        return int(self._pt_bv)

    def __invert__(self) -> int:
        return ~int(self)

    def __lt__(self, other) -> bool:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) < other

    def __le__(self, other) -> bool:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) <= other

    def __eq__(self, other) -> bool:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) == other

    def __ne__(self, other) -> bool:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) != other

    def __gt__(self, other) -> bool:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) > other

    def __ge__(self, other) -> bool:
        if isinstance(other, Numeric):
            other = int(other)
        return int(self) >= other

    def __hash__(self) -> int:
        return id(self)

    @classmethod
    def _pt_unpack(cls, _packed: int) -> Self:
        """
        Unpack the object from an integer
        :param packed: The value to unpack
        :return: The unpacked object
        """
        raise NotImplementedError

    def __copy__(self) -> Self:
        """
        Copy this object by unpacking and then packing it again
        :return: A copy of this object
        """
        return self._pt_unpack(int(self))

    def __deepcopy__(self, _memo: dict) -> Self:
        """
        Reuse __copy__,
        which should already be a deep copy for objects that pack and unpack cleanly.
        """
        return self.__copy__()
