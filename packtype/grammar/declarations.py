# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ..grammar.expression import DeclExpr
from ..types.alias import Alias
from ..types.assembly import Packing
from ..types.base import Base
from ..types.constant import Constant
from ..types.enum import Enum, EnumMode
from ..types.scalar import Scalar
from ..types.struct import Struct
from ..types.union import Union
from ..types.wrap import build_from_fields


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
    name: str


@dataclass()
class DeclAlias:
    position: Position
    name: str
    foreign: str

    def to_class(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> type[Alias]:
        return Alias[cb_resolve(self.foreign)]


@dataclass()
class DeclConstant:
    position: Position
    name: str
    width: DeclExpr
    expr: DeclExpr

    def to_instance(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> Constant:
        # Resolve width
        width = self.width
        if isinstance(width, DeclExpr):
            width = width.evaluate(cb_resolve)
        # Evaluate the expression referring to known constants
        value = self.expr.evaluate(cb_resolve)
        # Create instance
        if width is None:
            return Constant(default=value)
        else:
            return Constant[width](default=value)


@dataclass()
class DeclScalar:
    position: Position
    name: str
    signedness: type[Signed | Unsigned]
    width: DeclExpr

    def resolve_width(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> int:
        if isinstance(self.width, DeclExpr):
            return self.width.evaluate(cb_resolve)
        elif self.width is None:
            return 1
        else:
            raise Exception("Unexpected width type in DeclScalar")

    def to_field_def(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> tuple[type[Scalar], int | None]:
        return (
            self.to_class(cb_resolve),
            None,
        )

    def to_class(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> type[Scalar]:
        return Scalar[
            self.resolve_width(cb_resolve),
            (self.signedness is Signed),
        ]


@dataclass()
class DeclEnum:
    position: Position
    name: str
    mode: EnumMode
    width: DeclExpr | None
    description: Description | None
    values: list

    def to_class(
        self,
        source_file: Path,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> type[Enum]:
        # Resolve width
        width = self.width
        if isinstance(width, DeclExpr):
            width = width.evaluate(cb_resolve)
        # Process entries
        entries = {}
        for value in self.values:
            if isinstance(value, DeclConstant):
                entries[value.name] = (
                    Constant,
                    None if value.expr is None else value.expr.evaluate(cb_resolve),
                )
            elif isinstance(value, str):
                entries[value] = (Constant, None)
            else:
                raise ValueError(f"Unexpected enum value name: {value}")
        return build_from_fields(
            Enum,
            self.name,
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
    ref: str


@dataclass()
class DeclStruct:
    position: Position
    name: str
    packing: Packing
    width: DeclExpr | None
    description: Description | None
    fields: list[str]

    def to_class(
        self,
        source_file: Path,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> type[Struct]:
        # Resolve width
        width = self.width
        if isinstance(width, DeclExpr):
            width = width.evaluate(cb_resolve)
        # Process entries
        fields = {}
        for fdecl in self.fields:
            if isinstance(fdecl, DeclScalar):
                fields[fdecl.name] = fdecl.to_field_def(cb_resolve)
            elif isinstance(fdecl, DeclField):
                fields[fdecl.name] = (cb_resolve(fdecl.ref), None)
            else:
                raise ValueError(f"Unexpected struct field name: {fdecl}")
        return build_from_fields(
            Struct,
            self.name,
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
    name: str
    description: Description | None
    fields: list

    def to_class(
        self,
        source_file: Path,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> type[Union]:
        # Process entries
        fields = {}
        for fdecl in self.fields:
            if isinstance(fdecl, DeclScalar):
                fields[fdecl.name] = fdecl.to_field_def(cb_resolve)
            elif isinstance(fdecl, DeclField):
                fields[fdecl.name] = (cb_resolve(fdecl.ref), None)
            else:
                raise ValueError(f"Unexpected struct field name: {fdecl}")
        return build_from_fields(
            Union,
            self.name,
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
