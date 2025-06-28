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

from dataclasses import dataclass
from typing import Callable, Type

from packtype.base import Base
from packtype.grammar.expression import DeclExpr
from packtype.constant import Constant
from packtype.scalar import Scalar
from packtype.enum import Enum, EnumMode
from packtype.struct import Struct
from packtype.assembly import Packing
from packtype.union import Union
from packtype.wrap import build_from_fields


class Signed:
    pass


class Unsigned:
    pass


@dataclass()
class Position:
    line: int
    column: int


@dataclass()
class DeclImport:
    position: Position
    package: str
    type: str


@dataclass()
class DeclAlias:
    position: Position
    local: str
    foreign: str


@dataclass()
class DeclConstant:
    position: Position
    type: str
    width: DeclExpr
    expr: DeclExpr

    def to_instance(self, cb_rslv_const: Callable[[str, ], int]) -> Constant:
        # Resolve width
        width = self.width
        if isinstance(width, DeclExpr):
            width = width.evaluate(cb_rslv_const)
        # Evaluate the expression referring to known constants
        value = self.expr.evaluate(cb_rslv_const)
        # Create instance
        if width is None:
            return Constant(default=value)
        else:
            return Constant[width](default=value)


@dataclass()
class DeclScalar:
    position: Position
    type: str
    signedness: Type[Signed | Unsigned]
    width: DeclExpr

    def resolve_width(self, cb_rslv_const: Callable[[str, ], int]) -> int:
        if isinstance(self.width, DeclExpr):
            return self.width.evaluate(cb_rslv_const)
        elif self.width is None:
            return 1
        else:
            breakpoint()

    def to_field_def(
        self,
        cb_rslv_const: Callable[[str, ], int],
    ) -> tuple[Type[Scalar], int | None]:
        return (
            self.to_class(cb_rslv_const, lambda _: None),
            None,
        )

    def to_class(
        self,
        cb_rslv_const: Callable[[str, ], int],
        cb_rslv_type: Callable[[str, ], Type[Base]],
    ) -> Type[Scalar]:
        try:
            return Scalar[
                self.resolve_width(cb_rslv_const),
                (self.signedness is Signed),
            ]
        except:
            breakpoint()


@dataclass()
class DeclEnum:
    position: Position
    type: str
    mode: EnumMode
    width: DeclExpr | None
    description: str
    values: list

    def to_class(
        self,
        cb_rslv_const: Callable[[str, ], int],
        cb_rslv_type: Callable[[str, ], Type[Base]],
    ) -> Type[Enum]:
        # Resolve width
        width = self.width
        if isinstance(width, DeclExpr):
            width = width.evaluate(cb_rslv_const)
        # Process entries
        entries = {}
        for value in self.values:
            if isinstance(value, DeclConstant):
                entries[value.type] = (
                    Constant,
                    None if value.expr is None else value.expr.evaluate(cb_rslv_const)
                )
            elif isinstance(value, str):
                entries[value] = (Constant, None)
            else:
                raise ValueError(f"Unexpected enum value type: {value}")
        return build_from_fields(
            Enum,
            self.type,
            fields=entries,
            kwds={
                "mode": self.mode,
                "width": width,
            },
            doc_str=self.description,
        )


@dataclass()
class DeclField:
    position: Position
    name: str
    type: str


@dataclass()
class DeclStruct:
    position: Position
    type: str
    packing: Packing
    width: DeclExpr | None
    description: str
    fields: list[str]

    def to_class(
        self,
        cb_rslv_const: Callable[[str, ], int],
        cb_rslv_type: Callable[[str, ], Type[Base]],
    ) -> Type[Struct]:
        # Resolve width
        width = self.width
        if isinstance(width, DeclExpr):
            width = width.evaluate(cb_rslv_const)
        # Process entries
        fields = {}
        for fdecl in self.fields:
            if isinstance(fdecl, DeclScalar):
                fields[fdecl.type] = fdecl.to_field_def(cb_rslv_const)
            elif isinstance(fdecl, DeclField):
                fields[fdecl.name] = (cb_rslv_type(fdecl.type), None)
            else:
                raise ValueError(f"Unexpected struct field type: {fdecl}")
        return build_from_fields(
            Struct,
            self.type,
            fields=fields,
            kwds={
                "width": width,
                "packing": self.packing,
            },
            doc_str=self.description,
        )


@dataclass()
class DeclUnion:
    position: Position
    type: str
    description: str
    fields: list

    def to_class(
        self,
        cb_rslv_const: Callable[[str, ], int],
        cb_rslv_type: Callable[[str, ], Type[Base]],
    ) -> Type[Union]:
        # Process entries
        fields = {}
        for fdecl in self.fields:
            if isinstance(fdecl, DeclScalar):
                fields[fdecl.type] = fdecl.to_field_def(cb_rslv_const)
            elif isinstance(fdecl, DeclField):
                fields[fdecl.name] = (cb_rslv_type(fdecl.type), None)
            else:
                raise ValueError(f"Unexpected struct field type: {fdecl}")
        return build_from_fields(
            Union,
            self.type,
            fields=fields,
            kwds={},
            doc_str=self.description,
        )


@dataclass()
class DeclPackage:
    position: Position
    name: str
    description: str
    declarations: list
