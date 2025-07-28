# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ..common.expression import Expression
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
class Modifier:
    option: str
    value: str


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
    width: Expression
    expr: Expression
    description: Description | None = None

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
        if isinstance(width, Expression):
            width = width.evaluate(cb_resolve)
        # Evaluate the expression referring to known constants
        value = self.expr.evaluate(cb_resolve)
        # Create instance
        if width is None:
            const = Constant(default=value)
        else:
            const = Constant[width](default=value)
        # Attach optional description
        const.__doc__ = str(self.description) if self.description else None
        return const


@dataclass()
class DeclScalar:
    position: Position
    name: str
    signedness: type[Signed | Unsigned]
    width: Expression
    description: Description | None = None

    def resolve_width(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> int:
        if isinstance(self.width, Expression):
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
        scalar_cls = Scalar[
            self.resolve_width(cb_resolve),
            (self.signedness is Signed),
        ]
        scalar_cls.__doc__ = str(self.description) if self.description else None
        return scalar_cls


@dataclass()
class DeclEnum:
    position: Position
    name: str
    mode: EnumMode
    width: Expression | None
    description: Description | None
    modifiers: list[Modifier] | None
    values: list

    def get_modifiers(self) -> dict[str, str]:
        return {mod.option: mod.value for mod in (self.modifiers or {})}

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
        if isinstance(width, Expression):
            width = width.evaluate(cb_resolve)
        # Process entries
        doc_strs = {}
        entries = {}
        for value in self.values:
            if isinstance(value, DeclConstant):
                entries[value.name] = (
                    Constant,
                    None if value.expr is None else value.expr.evaluate(cb_resolve),
                )
                doc_strs[value.name] = str(value.description) if value.description else None
            elif isinstance(value, str):
                entries[value] = (Constant, None)
            else:
                raise ValueError(f"Unexpected enum value name: {value}")
        # Build the enum
        built = build_from_fields(
            Enum,
            self.name,
            fields=entries,
            kwds={
                "mode": self.mode,
                "width": width,
                **self.get_modifiers(),
            },
            doc_str=str(self.description) if self.description else None,
            source=(source_file.as_posix() if source_file else "N/A", self.position.line),
        )
        # Back-annotate the docstrings
        for name, doc_str in doc_strs.items():
            if doc_str is not None:
                getattr(built, name).__doc__ = doc_str
        # Return the built class
        return built


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
    width: Expression | None
    description: Description | None
    modifiers: list[Modifier] | None
    fields: list[str]

    def get_modifiers(self) -> dict[str, str]:
        return {mod.option: mod.value for mod in (self.modifiers or {})}

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
        if isinstance(width, Expression):
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
                **self.get_modifiers(),
            },
            doc_str=str(self.description) if self.description else None,
            source=(source_file.as_posix() if source_file else "N/A", self.position.line),
        )


@dataclass()
class DeclUnion:
    position: Position
    name: str
    description: Description | None
    modifiers: list[Modifier] | None
    fields: list

    def get_modifiers(self) -> dict[str, str]:
        return {mod.option: mod.value for mod in (self.modifiers or {})}

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
            kwds=self.get_modifiers(),
            doc_str=str(self.description) if self.description else None,
            source=(source_file.as_posix() if source_file else "N/A", self.position.line),
        )


@dataclass()
class DeclPackage:
    position: Position
    name: str
    description: Description | None
    modifiers: list[Modifier] | None
    declarations: list

    def get_modifiers(self) -> dict[str, str]:
        return {mod.option: mod.value for mod in (self.modifiers or {})}
