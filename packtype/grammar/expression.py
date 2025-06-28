# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
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

from typing import Self, Callable


class DeclExpr:

    def __init__(
        self,
        lhs: str | int | float | Self = None,
        rhs: str | int | float | Self = None,
        operator: Callable | None = None,
    ):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def evaluate(self, cb_lookup: Callable[[str, ], int]) -> int:
        # Flatten LHS
        lhs = self.lhs
        if isinstance(self.lhs, DeclExpr):
            lhs = self.lhs.evaluate(cb_lookup)
        elif isinstance(self.lhs, str):
            lhs = cb_lookup(self.lhs)
        # If operator exists
        if self.operator:
            # Flatten RHS
            rhs = self.rhs
            if isinstance(self.rhs, DeclExpr):
                rhs = self.rhs.evaluate(cb_lookup)
            elif isinstance(self.rhs, str):
                rhs = cb_lookup(self.rhs)
            # Apply operator
            return self.operator(lhs, rhs)
        # Otherwise just return LHS
        else:
            return lhs

    def _wrap(self, operator: Callable, lhs: str | int | float | Self = None, rhs: str | int | float | Self = None) -> Self:
        return DeclExpr(lhs=lhs or self, rhs=rhs, operator=operator)

    def __repr__(self):
        return self.__str__()

    def __str__(self) -> str:
        if self.operator is None:
            return str(self.lhs)
        else:
            return f"{self.lhs} {self.operator} {self.rhs}"

    @classmethod
    def operate(
        cls,
        lhs: str | int | float | Self,
        operator: str,
        rhs: str | int | float | Self,
    ) -> Callable:
        match operator:
            case "+":
                return cls(lhs).__add__(rhs)
            case "-":
                return cls(lhs).__sub__(rhs)
            case "*":
                return cls(lhs).__mul__(rhs)
            case "/":
                return cls(lhs).__truediv__(rhs)
            case "//":
                return cls(lhs).__floordiv__(rhs)
            case "%":
                return cls(lhs).__mod__(rhs)
            case "divmod":
                return cls(lhs).__divmod__(rhs)
            case "**":
                return cls(lhs).__pow__(rhs)
            case "<<":
                return cls(lhs).__lshift__(rhs)
            case ">>":
                return cls(lhs).__rshift__(rhs)
            case "&":
                return cls(lhs).__and__(rhs)
            case "^":
                return cls(lhs).__xor__(rhs)
            case "|":
                return cls(lhs).__or__(rhs)
            case "~":
                return cls(lhs).__invert__(rhs)
            case "<":
                return cls(lhs).__lt__(rhs)
            case "<=":
                return cls(lhs).__le__(rhs)
            case "==":
                return cls(lhs).__eq__(rhs)
            case "!=":
                return cls(lhs).__ne__(rhs)
            case ">":
                return cls(lhs).__gt__(rhs)
            case ">=":
                return cls(lhs).__ge__(rhs)
            case _:
                raise ValueError(f"Operator '{operator}' is not supported by operate")

    def __add__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x + y, rhs=other)

    def __sub__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x - y, rhs=other)

    def __mul__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x * y, rhs=other)

    def __truediv__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x / y, rhs=other)

    def __floordiv__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x // y, rhs=other)

    def __mod__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x % y, rhs=other)

    def __divmod__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: (x // y, x % y), rhs=other)

    def __pow__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x ** y, rhs=other)

    def __lshift__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x << y, rhs=other)

    def __rshift__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x >> y, rhs=other)

    def __and__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x & y, rhs=other)

    def __xor__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x ^ y, rhs=other)

    def __or__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x | y, rhs=other)

    def __radd__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x + y, lhs=other, rhs=self)

    def __rsub__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x - y, lhs=other, rhs=self)

    def __rmul__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x * y, lhs=other, rhs=self)

    def __rtruediv__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x / y, lhs=other, rhs=self)

    def __rfloordiv__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x // y, lhs=other, rhs=self)

    def __rmod__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x % y, lhs=other, rhs=self)

    def __rdivmod__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: (x // y, x % y), lhs=other, rhs=self)

    def __rpow__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x ** y, lhs=other, rhs=self)

    def __rlshift__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x << y, lhs=other, rhs=self)

    def __rrshift__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x >> y, lhs=other, rhs=self)

    def __rand__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x & y, lhs=other, rhs=self)

    def __rxor__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x ^ y, lhs=other, rhs=self)

    def __ror__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x | y, lhs=other, rhs=self)

    def __iadd__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x + y, rhs=other)

    def __isub__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x - y, rhs=other)

    def __imul__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x * y, rhs=other)

    def __itruediv__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x / y, rhs=other)

    def __ifloordiv__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x // y, rhs=other)

    def __imod__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x % y, rhs=other)

    def __ipow__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x ** y, rhs=other)

    def __ilshift__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x << y, rhs=other)

    def __irshift__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x >> y, rhs=other)

    def __iand__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x & y, rhs=other)

    def __ixor__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x ^ y, rhs=other)

    def __ior__(self, other: int | Self) -> int:
        return self._wrap(lambda x, y: x | y, rhs=other)

    def __neg__(self) -> int:
        return self._wrap(lambda x, _: -1 * x)

    def __pos__(self) -> int:
        return self._wrap(lambda x, _: x)

    def __abs__(self) -> int:
        return self._wrap(lambda x, _: abs(x))

    def __invert__(self) -> int:
        return self._wrap(lambda x, _: ~x)

    def __lt__(self, other: int | Self) -> bool:
        return self._wrap(lambda x, y: x < y, rhs=other)

    def __le__(self, other: int | Self) -> bool:
        return self._wrap(lambda x, y: x <= y, rhs=other)

    def __eq__(self, other: int | Self) -> bool:
        return self._wrap(lambda x, y: x == y, rhs=other)

    def __ne__(self, other: int | Self) -> bool:
        return self._wrap(lambda x, y: x != y, rhs=other)

    def __gt__(self, other: int | Self) -> bool:
        return self._wrap(lambda x, y: x > y, rhs=other)

    def __ge__(self, other: int | Self) -> bool:
        return self._wrap(lambda x, y: x >= y, rhs=other)
