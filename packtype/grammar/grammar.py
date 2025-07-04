# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import functools
from pathlib import Path
from typing import Type

from lark import Lark
from lark.exceptions import UnexpectedToken

from ..constant import Constant
from .declarations import (
    DeclImport,
    DeclAlias,
    DeclConstant,
    DeclScalar,
    DeclEnum,
    DeclStruct,
    DeclUnion,
    Position,
)
from .transformer import PacktypeTransformer
from ..package import Package
from ..base import Base
from ..wrap import build_from_fields


@functools.cache
def create_parser():
    parser = Lark.open(
        Path(__file__).parent / "packtype.lark",
        start="root",
        parser="lalr",
        propagate_positions=True,
    )
    return parser


class ParseError(Exception):
    """Exception raised when parsing a Packtype definition fails."""
    pass


class RedefinitionError(Exception):
    """Exception raised when a type or constant name is repeated."""
    pass


def parse_string(
    definition: str,
    namespaces: dict[str, Package] | None = None,
    source: Path | None = None,
) -> Package:
    """
    Parse a Packtype definition from a string producing a Package object.

    :param definition: The Packtype definition as a string.
    :param namespaces: A dictionary of known packages to resolve imports.
    :param source:     An optional source path for error reporting and associating
                       each declaration with its source file.
    :return:           A Package object representing the parsed definition.
    """
    # If no namespaces are provided, use an empty dict
    namespaces = namespaces or {}
    # Parse the definition
    try:
        defn = PacktypeTransformer().transform(create_parser().parse(definition))
    except UnexpectedToken as exc:
        raise ParseError(
            f"Failed to parse {source.name if source else 'input'} on line {exc.line}: "
            f"\n\n{exc.get_context(definition)}\n{exc}"
        ) from exc
    # Gather declarations
    known_constants: dict[str, tuple[Constant, Position]] = {}
    known_types: dict[str, tuple[Type[Base], Position]] = {}

    def _check_collision(name: str) -> None:
        nonlocal known_types, known_constants
        if (existing := known_types.get(name, None)) is not None:
            ref, pos = existing
            raise RedefinitionError(
                f"'{name}' is already defined as a {ref.__name__} in "
                f"{source or 'N/A'} on line {pos.line}"
            )
        elif (existing := known_constants.get(name, None)) is not None:
            _, pos = existing
            raise RedefinitionError(
                f"'{name}' is already defined as a constant in {source or 'N/A'} "
                f"on line {pos.line}"
            )

    def _rslv_const(name: str) -> int:
        nonlocal known_constants
        if name in known_constants:
            return known_constants[name][0]
        raise ParseError(f"Failed to resolve '{name}' to a known constant")

    def _rslv_type(name: str) -> Type[Base]:
        nonlocal known_types
        if name in known_types:
            return known_types[name][0]
        raise ParseError(f"Failed to resolve '{name}' to a known type")

    # Create the package
    package : Package = build_from_fields(
        base=Package,
        cname=defn.name,
        fields={},
        kwds={},
        doc_str=str(defn.description) if defn.description else None,
    )

    # Run through the declarations
    for decl in defn.declarations:
        match decl:
            # Imports
            case DeclImport():
                # Resolve the package
                if (foreign_pkg := namespaces.get(decl.package, None)) is None:
                    raise ImportError(f"Unknown package '{decl.package}'")
                # Resolve the type
                if (foreign_type := getattr(foreign_pkg, decl.type, None)) is None:
                    raise ImportError(f"'{decl.type}' not declared in package '{decl.package}'")
                # Check for name collisions
                _check_collision(decl.type)
                # Remember this type
                if isinstance(foreign_type, Constant):
                    known_constants[decl.type] = (foreign_type, decl.position)
                else:
                    known_types[decl.type] = (foreign_type, decl.position)
            # Aliases
            case DeclAlias():
                package._pt_attach(
                    scalar := decl.to_class(_rslv_const, _rslv_type),
                    name=decl.type,
                )
                # Check for name collisions
                _check_collision(decl.type)
                # Remember this type
                known_types[decl.type] = (scalar, decl.position)
            # Build constants
            case DeclConstant():
                package._pt_attach_constant(
                    decl.type,
                    constant := decl.to_instance(_rslv_const)
                )
                # Check for name collisions
                _check_collision(decl.type)
                # Remember this constant
                known_constants[decl.type] = (constant, decl.position)
            # Build aliases and scalars
            case DeclScalar() | DeclAlias():
                package._pt_attach(
                    obj := decl.to_class(_rslv_const, _rslv_type),
                    name=decl.type,
                )
                # Check for name collisions
                _check_collision(decl.type)
                # Remember this type
                known_types[decl.type] = (obj, decl.position)
            # Build enums, structs, and unions
            case DeclEnum() | DeclStruct() | DeclUnion():
                package._pt_attach(obj := decl.to_class(
                    source,
                    _rslv_const,
                    _rslv_type,
                ))
                # Check for name collisions
                _check_collision(decl.type)
                # Remember this type
                known_types[decl.type] = (obj, decl.position)
            case _:
                raise Exception(f"Unhandled declaration: {decl}")

    return package


def parse(path: Path, namespaces: dict[str, Package] | None = None) -> Package:
    """
    Parse a Packtype definition from a file path producing a Package object.

    :param path:       The path to the Packtype definition file.
    :param namespaces: A dictionary of known packages to resolve imports.
    :return:           A Package object representing the parsed definition.
    """
    with path.open("r", encoding="utf-8") as fh:
        return parse_string(fh.read(), namespaces, path)
