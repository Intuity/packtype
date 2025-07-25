# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Callable
from typing import Any, Self


class Expression:
    """Encapsulates an expression that can be evaluated at a later time"""

    OP_ADD = "+"
    OP_SUB = "-"
    OP_MUL = "*"
    OP_TRUEDIV = "/"
    OP_FLOORDIV = "//"
    OP_MOD = "%"
    OP_POW = "**"
    OP_LSHIFT = "<<"
    OP_RSHIFT = ">>"
    OP_AND = "&"
    OP_XOR = "^"
    OP_OR = "|"
    OP_INV = "~"
    OP_LT = "<"
    OP_LE = "<="
    OP_EQ = "=="
    OP_NE = "!="
    OP_GT = ">"
    OP_GE = ">="

    # Matched to: https://docs.python.org/3/reference/expressions.html#operator-precedence
    OP_PRECEDENCE = [
        OP_POW,
        OP_INV,
        OP_MUL,
        OP_TRUEDIV,
        OP_FLOORDIV,
        OP_MOD,
        OP_ADD,
        OP_SUB,
        OP_LSHIFT,
        OP_RSHIFT,
        OP_AND,
        OP_XOR,
        OP_OR,
        OP_LT,
        OP_LE,
        OP_GT,
        OP_GE,
        OP_NE,
        OP_EQ,
    ]

    def __init__(
        self,
        lhs: str | int | float | Self | None = None,
        rhs: str | int | float | Self | None = None,
        operator: Callable | None = None,
    ):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def evaluate(self, cb_lookup: Callable[[str], int]) -> int:
        # Flatten LHS
        lhs = self.lhs
        if isinstance(self.lhs, Expression | ExpressionFunction):
            lhs = self.lhs.evaluate(cb_lookup)
        elif isinstance(self.lhs, str):
            lhs = cb_lookup(self.lhs)
        # If operator exists
        if self.operator:
            # Flatten RHS
            rhs = self.rhs
            if isinstance(self.rhs, Expression | ExpressionFunction):
                rhs = self.rhs.evaluate(cb_lookup)
            elif isinstance(self.rhs, str):
                rhs = cb_lookup(self.rhs)
            # Apply operator
            return int(self.operator(lhs, rhs))
        # Check if the LHS is a _PT_BASE attribute
        elif hasattr(lhs, "_PT_BASE") and type(lhs).__name__ != "Constant":
            return lhs
        # Otherwise, cast LHS to an integer
        else:
            return int(lhs)

    def _wrap(
        self,
        operator: Callable,
        lhs: str | int | float | Self | None = None,
        rhs: str | int | float | Self | None = None,
    ) -> Self:
        return Expression(lhs=lhs or self, rhs=rhs, operator=operator)

    def __repr__(self):
        return self.__str__()

    def __str__(self) -> str:
        if self.operator is None:
            return str(self.lhs)
        else:
            return f"({self.lhs}) {self.operator} ({self.rhs})"

    @classmethod
    def digest(cls, expr: list[str | int | float | Self]) -> Self:
        """
        Digest an expression based on operator precedence, and progressively
        reduce it to a single Expression instance. Note that this does not handle
        brackets in the expression as this is expected to be handled by the
        parser before this point.

        :param expr: Expression as a list of strings (operators or variables),
                     integers, floats, or Expression instances.
        :return: A single Expression instance representing the expression.
        """
        # Take a copy so as not to mutate the original
        expr = list(expr)
        # Search for each operator in precedence order
        for search_op in cls.OP_PRECEDENCE:
            # If only a single term remains, break out early
            if len(expr) == 1:
                break
            # Look for every position an operator could exist (every other term)
            offset = 0
            for op_pos in [x for x in range(1, len(expr), 2) if expr[x] == search_op]:
                # Replace the term with a Expression instance
                *before, lhs = expr[: op_pos + offset]
                rhs, *after = expr[op_pos + offset + 1 :]
                expr = [*before, cls.operate(lhs, search_op, rhs), *after]
                offset -= 2
        # Ensure that even a single term is returned as a Expression instance
        expr = expr[0]
        if not isinstance(expr, cls):
            expr = cls(lhs=expr)
        return expr

    @classmethod
    def operate(
        cls,
        lhs: str | int | float | Self,
        operator: str,
        rhs: str | int | float | Self,
    ) -> Callable:
        match operator:
            case cls.OP_ADD:
                return cls(lhs).__add__(rhs)
            case cls.OP_SUB:
                return cls(lhs).__sub__(rhs)
            case cls.OP_MUL:
                return cls(lhs).__mul__(rhs)
            case cls.OP_TRUEDIV:
                return cls(lhs).__truediv__(rhs)
            case cls.OP_FLOORDIV:
                return cls(lhs).__floordiv__(rhs)
            case cls.OP_MOD:
                return cls(lhs).__mod__(rhs)
            case cls.OP_POW:
                return cls(lhs).__pow__(rhs)
            case cls.OP_LSHIFT:
                return cls(lhs).__lshift__(rhs)
            case cls.OP_RSHIFT:
                return cls(lhs).__rshift__(rhs)
            case cls.OP_AND:
                return cls(lhs).__and__(rhs)
            case cls.OP_XOR:
                return cls(lhs).__xor__(rhs)
            case cls.OP_OR:
                return cls(lhs).__or__(rhs)
            case cls.OP_INV:
                return cls(lhs).__invert__(rhs)
            case cls.OP_LT:
                return cls(lhs).__lt__(rhs)
            case cls.OP_LE:
                return cls(lhs).__le__(rhs)
            case cls.OP_EQ:
                return cls(lhs).__eq__(rhs)
            case cls.OP_NE:
                return cls(lhs).__ne__(rhs)
            case cls.OP_GT:
                return cls(lhs).__gt__(rhs)
            case cls.OP_GE:
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
        return self._wrap(lambda x, y: x**y, rhs=other)

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
        return self._wrap(lambda x, y: x**y, lhs=other, rhs=self)

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
        return self._wrap(lambda x, y: x**y, rhs=other)

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


class ExpressionFunction:
    """Encapsulates a function call within an expression"""

    def __init__(
        self,
        operator: Callable[[Any], Any],
        *args: str | int | float | Self | Expression,
    ) -> None:
        self.operator = operator
        self.args = args

    def evaluate(self, cb_lookup: Callable[[str], int]) -> int:
        # Resolve all arguments
        resolved = []
        for arg in self.args:
            if isinstance(arg, Expression | ExpressionFunction):
                resolved.append(arg.evaluate(cb_lookup))
            else:
                resolved.append(arg)
        # Perform the operation
        return self.operator(*resolved)
