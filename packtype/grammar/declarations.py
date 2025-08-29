# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ..common.expression import Expression
from ..types.alias import Alias
from ..types.array import ArraySpec
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
class ForeignRef:
    package: str
    name: str


@dataclass()
class DeclImport:
    position: Position
    foreign: ForeignRef


@dataclass()
class DeclDimensions:
    dimensions: list[int]

    def resolve(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> list[int]:
        eval_dims = []
        for raw_dim in self.dimensions:
            if isinstance(raw_dim, Expression):
                eval_dims.append(raw_dim.evaluate(cb_resolve))
            else:
                raise Exception("Unexpected width type in DeclScalar")
        return eval_dims


@dataclass()
class DeclAlias:
    position: Position
    name: str
    foreign: str
    dimensions: DeclDimensions | None = None
    description: Description | None = None

    def to_class(
        self,
        cb_resolve: Callable[
            [
                str,
            ],
            int | type[Base],
        ],
    ) -> type[Alias] | ArraySpec:
        entity = cb_resolve(self.foreign)
        if self.dimensions:
            for dim in self.dimensions.resolve(cb_resolve):
                entity = entity[dim]
            return entity
        else:
            return Alias[entity]


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
    dimensions: DeclDimensions
    description: Description | None = None

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
        entity = None
        for dim in self.dimensions.resolve(cb_resolve):
            if entity is None:
                entity = Scalar[dim, (self.signedness is Signed)]
            else:
                entity = entity[dim]
        entity.__doc__ = str(self.description) if self.description else None
        return entity


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
    dimensions: DeclDimensions | None = None
    description: Description | None = None


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
                ftype = cb_resolve(fdecl.ref)
                if fdecl.dimensions:
                    for dim in fdecl.dimensions.resolve(cb_resolve):
                        ftype = ftype[dim]
                fields[fdecl.name] = (ftype, None)
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
                ftype = cb_resolve(fdecl.ref)
                if fdecl.dimensions:
                    for dim in fdecl.dimensions.resolve(cb_resolve):
                        ftype = ftype[dim]
                fields[fdecl.name] = (ftype, None)
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
