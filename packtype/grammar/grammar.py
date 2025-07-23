# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import functools
import inspect
from pathlib import Path

from lark import Lark
from lark.exceptions import UnexpectedToken

from ..common.logging import get_log
from ..types.base import Base
from ..types.constant import Constant
from ..types.package import Package
from ..types.wrap import build_from_fields
from .declarations import (
    DeclAlias,
    DeclConstant,
    DeclEnum,
    DeclImport,
    DeclScalar,
    DeclStruct,
    DeclUnion,
    Position,
)
from .transformer import PacktypeTransformer


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


class UnknownEntityError(Exception):
    """Exception raised when a constant or type is referenced but not defined."""

    pass


class RedefinitionError(Exception):
    """Exception raised when a type or constant name is repeated."""

    pass


def parse_string(
    definition: str,
    namespaces: dict[str, Package] | None = None,
    constant_overrides: dict[str, int] | None = None,
    source: Path | None = None,
) -> Package:
    """
    Parse a Packtype definition from a string producing a Package object.

    :param definition:         The Packtype definition as a string.
    :param namespaces:         A dictionary of known packages to resolve imports.
    :param source:             An optional source path for error reporting and
                               associating each declaration with its source file.
    :param constant_overrides: Optional overrides for constants defined within
                               the package, where the key must precisely match
                               the constant's name
    :return:                   A Package object representing the parsed definition.
    """
    # If no namespaces are provided, use an empty dict
    namespaces = namespaces or {}
    # If no constant overrides are provided, use an empty dict
    constant_overrides = constant_overrides or {}
    # Parse the definition
    try:
        defn = PacktypeTransformer().transform(create_parser().parse(definition))
    except UnexpectedToken as exc:
        raise ParseError(
            f"Failed to parse {source.name if source else 'input'} on line {exc.line}: "
            f"\n\n{exc.get_context(definition)}\n{exc}"
        ) from exc
    # Gather declarations
    known_entities: dict[str, tuple[type[Base] | Constant, Position]] = {}

    def _check_collision(name: str) -> None:
        nonlocal known_entities
        if (existing := known_entities.get(name, None)) is not None:
            ref, pos = existing
            ref_name = ref.__name__ if inspect.isclass(ref) else type(ref).__name__
            raise RedefinitionError(
                f"'{name}' is already defined as a {ref_name} in {source or 'N/A'} "
                f"on line {pos.line}"
            )

    def _resolve(name: str) -> int:
        nonlocal known_entities
        if name in known_entities:
            return known_entities[name][0]
        raise UnknownEntityError(f"Failed to resolve '{name}' to a known constant or type")

    # Create the package
    package: Package = build_from_fields(
        base=Package,
        cname=defn.name,
        fields={},
        kwds=defn.get_modifiers(),
        doc_str=str(defn.description) if defn.description else None,
        source=(source.as_posix() if source else "N/A", defn.position.line),
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
                if (foreign_type := getattr(foreign_pkg, decl.name, None)) is None:
                    raise ImportError(f"'{decl.name}' not declared in package '{decl.package}'")
                # Check for name collisions
                _check_collision(decl.name)
                # Remember this type
                if isinstance(foreign_type, Constant):
                    known_entities[decl.name] = (foreign_type, decl.position)
                else:
                    known_entities[decl.name] = (foreign_type, decl.position)
            # Aliases
            case DeclAlias():
                package._pt_attach(
                    scalar := decl.to_class(_resolve),
                    name=decl.name,
                )
                # Check for name collisions
                _check_collision(decl.name)
                # Remember this type
                known_entities[decl.name] = (scalar, decl.position)
            # Build constants
            case DeclConstant():
                package._pt_attach_constant(decl.name, constant := decl.to_instance(_resolve))
                # Check for name collisions
                _check_collision(decl.name)
                # Check for a constant override
                if decl.name in constant_overrides:
                    get_log().debug(
                        f"Overriding constant '{decl.name}' with value "
                        f"{constant_overrides[decl.name]}"
                    )
                    constant._pt_set(int(constant_overrides[decl.name]))
                # Remember this constant
                known_entities[decl.name] = (constant, decl.position)
            # Build aliases and scalars
            case DeclScalar() | DeclAlias():
                package._pt_attach(
                    obj := decl.to_class(_resolve),
                    name=decl.name,
                )
                # Check for name collisions
                _check_collision(decl.name)
                # Remember this type
                known_entities[decl.name] = (obj, decl.position)
            # Build enums, structs, and unions
            case DeclEnum() | DeclStruct() | DeclUnion():
                package._pt_attach(obj := decl.to_class(source, _resolve))
                # Check for name collisions
                _check_collision(decl.name)
                # Remember this type
                known_entities[decl.name] = (obj, decl.position)
            case _:
                raise Exception(f"Unhandled declaration: {decl}")

    # Check for overrides that don't match up
    for name in constant_overrides.keys():
        if not hasattr(package, name):
            raise UnknownEntityError(
                f"Constant override '{name}' does not match any defined constant "
                f"in package '{package.__name__}'"
            )
        elif not isinstance(getattr(package, name), Constant):
            raise TypeError(
                f"Constant override '{name}' does not match a constant in package "
                f"'{package.__name__}', found {getattr(package, name).__name__}"
            )

    return package


def parse(
    path: Path,
    namespaces: dict[str, Package] | None = None,
    constant_overrides: dict[str, int] | None = None,
) -> Package:
    """
    Parse a Packtype definition from a file path producing a Package object.

    :param path:               The path to the Packtype definition file.
    :param namespaces:         A dictionary of known packages to resolve imports.
    :param constant_overrides: Optional overrides for constants defined within
                               the package, where the key must precisely match
                               the constant's name.
    :return:                   A Package object representing the parsed definition.
    """
    with path.open("r", encoding="utf-8") as fh:
        return parse_string(fh.read(), namespaces, constant_overrides, path)
