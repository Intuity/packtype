# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Type

from ..alias import Alias
from ..base import Base
from ..grammar.expression import DeclExpr
from ..constant import Constant
from ..scalar import Scalar
from ..enum import Enum, EnumMode
from ..struct import Struct
from ..assembly import Packing
from ..union import Union
from ..wrap import build_from_fields


class Signed:
    pass


class Unsigned:
    pass


@dataclass()
class Description:
    text: str

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return self.__str__()


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
    type: str
    foreign: str

    def to_class(
        self,
        cb_rslv_const: Callable[[str, ], int],
        cb_rslv_type: Callable[[str, ], Type[Base]],
    ) -> Type[Alias]:
        return Alias[cb_rslv_type(self.foreign)]


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
        return Scalar[
            self.resolve_width(cb_rslv_const),
            (self.signedness is Signed),
        ]


@dataclass()
class DeclEnum:
    position: Position
    type: str
    mode: EnumMode
    width: DeclExpr | None
    description: Description | None
    values: list

    def to_class(
        self,
        source_file: Path,
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
            doc_str=str(self.description) if self.description else None,
            source=(source_file.as_posix() if source_file else "N/A", self.position.line),
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
    description: Description | None
    fields: list[str]

    def to_class(
        self,
        source_file: Path,
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
            doc_str=str(self.description) if self.description else None,
            source=(source_file.as_posix() if source_file else "N/A", self.position.line),
        )


@dataclass()
class DeclUnion:
    position: Position
    type: str
    description: Description | None
    fields: list

    def to_class(
        self,
        source_file: Path,
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
            doc_str=str(self.description) if self.description else None,
            source=(source_file.as_posix() if source_file else "N/A", self.position.line),
        )


@dataclass()
class DeclPackage:
    position: Position
    name: str
    description: Description | None
    declarations: list
