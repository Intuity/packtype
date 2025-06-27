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

from collections import namedtuple
from pathlib import Path
from enum import Enum, auto
from typing import Self, Callable

from lark import Lark, Transformer, v_args

from packtype.enum import EnumMode

GRAMMAR = Path(__file__).parent / "packtype.lark"
EXAMPLE = Path(__file__).parent / "example.pt"


class Signedness(Enum):
    UNSIGNED = auto()
    SIGNED = auto()


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


Position = namedtuple("Position", ["line", "column"])
DeclImport = namedtuple("DeclImport", ["position", "package", "type"])
DeclAlias = namedtuple("DeclAlias", ["position", "local", "foreign"])
DeclConstant = namedtuple("DeclConstant", ["position", "type", "width", "expr"])
DeclScalar = namedtuple("DeclScalar", ["position", "type", "signedness", "width"])
DeclEnum = namedtuple("DeclEnum", ["position", "type", "mode", "width", "description", "values"])
DeclField = namedtuple("DeclField", ["position", "name", "type"])
DeclStruct = namedtuple("DeclStruct", ["position", "name", "width", "description", "fields"])
DeclUnion = namedtuple("DeclUnion", ["position", "name", "description", "fields"])
DeclPackage = namedtuple("DeclPackage", ["position", "name", "description", "declarations"])


class PacktypeTransformer(Transformer):

    def SIGNED_INT(self, body):
        return int(body)

    def HEX(self, body):
        return int(body, 16)

    def OPERATOR(self, body):
        return str(body)

    def expr(self, body):
        if len(body) == 3:
            return DeclExpr.operate(*body)
        else:
            return DeclExpr(body[0])

    def signed(self, *_):
        return Signedness.SIGNED

    def unsigned(self, *_):
        return Signedness.UNSIGNED

    def enum_mode_indexed(self, *_):
        return EnumMode.INDEXED

    def enum_mode_onehot(self, *_):
        return EnumMode.ONE_HOT

    def enum_mode_gray(self, *_):
        return EnumMode.GRAY

    def CNAME(self, body):
        return str(body)

    def descr(self, body):
        return str(body[0]).strip('"')

    @v_args(meta=True)
    def decl_import(self, meta, body):
        return DeclImport(Position(meta.line, meta.column), *body)

    @v_args(meta=True)
    def decl_alias(self, meta, body):
        return DeclAlias(Position(meta.line, meta.column), *body)

    @v_args(meta=True)
    def decl_constant(self, meta, body):
        c_type, *remainder = body
        if c_type == "SIZED_CONSTANT":
            width, expr = remainder
        else:
            width = None
            expr = remainder[0]
        return DeclConstant(Position(meta.line, meta.column), c_type, width, expr)

    @v_args(meta=True)
    def field(self, meta, body):
        return body[0] if isinstance(body[0], DeclScalar) else DeclField(Position(meta.line, meta.column),*body)

    @v_args(meta=True)
    def decl_enum(self, meta, body):
        e_type, *remainder = body
        # Pickup mode if given
        if remainder and isinstance(remainder[0], EnumMode):
            mode, *remainder = remainder
        else:
            mode = EnumMode.INDEXED
        # Pickup width if given
        if remainder and isinstance(remainder[0], int):
            width, *remainder = remainder
        else:
            width = None
        # Pickup description if given
        if remainder and isinstance(remainder[0], str):
            description, *remainder = remainder
        else:
            description = None
        return DeclEnum(Position(meta.line, meta.column), e_type, mode, width, description, remainder)

    @v_args(meta=True)
    def decl_scalar(self, meta, body):
        s_type, *remainder = body
        # Pickup signedness
        if remainder and isinstance(remainder[0], Signedness):
            signed, *remainder = remainder
        else:
            signed = Signedness.UNSIGNED
        # Pickup width
        if remainder:
            width = remainder[0]
        else:
            width = 1
        return DeclScalar(Position(meta.line, meta.column), s_type, signed, width)

    @v_args(meta=True)
    def decl_struct(self, meta, body):
        # Extract width if given
        if isinstance(body[0], int):
            width, name, *remainder = body
        else:
            width = None
            name, *remainder = body
        # Extract description if given
        if isinstance(remainder[0], str):
            description, *fields = remainder
        else:
            description = None
            fields = remainder
        return DeclStruct(Position(meta.line, meta.column), name, width, description, fields)

    @v_args(meta=True)
    def decl_union(self, meta, body):
        # Extract name and description
        if isinstance(body[0], str):
            name, *remainder = body
            description = None
        else:
            name, description, *remainder = body
        # Fields are the rest of the body
        fields = remainder
        return DeclUnion(Position(meta.line, meta.column), name, description, fields)

    @v_args(meta=True)
    def decl_package(self, meta, body):
        p_name, *remainder = body
        # Extract description if given
        if isinstance(remainder[0], str):
            description, *remainder = remainder
        else:
            description = None
        return DeclPackage(Position(meta.line, meta.column), p_name, description, remainder)

parser = Lark.open(
    GRAMMAR,
    start="root",
    parser="lalr",
    propagate_positions=True,
)

ast = PacktypeTransformer().transform(parser.parse(EXAMPLE.read_text(encoding="utf-8")))

print(ast)

breakpoint()
