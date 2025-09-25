# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import functools
import inspect
from collections.abc import Iterable
from pathlib import Path

from lark import Lark
from lark.exceptions import UnexpectedToken, VisitError

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
    DeclInstance,
    DeclPackage,
    DeclScalar,
    DeclStruct,
    DeclUnion,
    ForeignRef,
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
    keep_expression: bool = False,
) -> Iterable[Package]:
    """
    Parse a Packtype definition from a string producing a Package object.

    :param definition:         The Packtype definition as a string.
    :param namespaces:         A dictionary of known packages to resolve imports.
    :param constant_overrides: Optional overrides for constants defined within
                               the package, where the key must precisely match
                               the constant's name
    :param source:             An optional source path for error reporting and
                               associating each declaration with its source file.
    :param keep_expression:    If True, expressions will be attached to constants
                               allowing them to be re-evaluated with new inputs.
    :yields:                   A Package object representing the parsed definition.
    """
    # If no namespaces are provided, use an empty dict
    namespaces = namespaces or {}
    # If no constant overrides are provided, use an empty dict
    constant_overrides = constant_overrides or {}
    # Parse the definition
    try:
        definitions = PacktypeTransformer().transform(create_parser().parse(definition))
    except UnexpectedToken as exc:
        raise ParseError(
            f"Failed to parse {source.name if source else 'input'} on line {exc.line}: "
            f"\n\n{exc.get_context(definition)}\n{exc}"
        ) from exc
    except VisitError as exc:
        raise exc.orig_exc from exc

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

    def _resolve(ref: str | ForeignRef) -> int:
        nonlocal known_entities
        if isinstance(ref, ForeignRef):
            if ref.package not in namespaces:
                raise UnknownEntityError(f"Failed to resolve package '{ref.package}'")
            if not hasattr(namespaces[ref.package], ref.name):
                raise UnknownEntityError(
                    f"Failed to resolve '{ref.name}' in package '{ref.package}'"
                )
            return getattr(namespaces[ref.package], ref.name)
        elif ref in known_entities:
            return known_entities[ref][0]
        raise UnknownEntityError(f"Failed to resolve '{ref}' to a known constant or type")

    for defn in [definitions] if isinstance(definitions, DeclPackage) else definitions:
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
                    # Check for name collisions
                    _check_collision(decl.foreign.name)
                    # Resolve the package
                    if (foreign_pkg := namespaces.get(decl.foreign.package, None)) is None:
                        raise ImportError(f"Unknown package '{decl.foreign.package}'")
                    # Resolve the type
                    if (foreign_type := getattr(foreign_pkg, decl.foreign.name, None)) is None:
                        raise ImportError(
                            f"'{decl.foreign.name}' not declared in package "
                            f"'{decl.foreign.package}'"
                        )
                    # Remember this type
                    if isinstance(foreign_type, Constant):
                        known_entities[decl.foreign.name] = (foreign_type, decl.position)
                    else:
                        known_entities[decl.foreign.name] = (foreign_type, decl.position)
                # Aliases
                case DeclAlias():
                    # Check for name collisions
                    _check_collision(decl.name)
                    # Attach to the package
                    package._pt_attach(
                        alias := decl.to_class(_resolve),
                        name=decl.name,
                    )
                    # Remember this type
                    known_entities[decl.name] = (alias, decl.position)
                # Build constants
                case DeclConstant():
                    # Check for name collisions
                    _check_collision(decl.name)
                    # Attach to the package
                    constant = decl.to_instance(_resolve)
                    if keep_expression:
                        constant._PT_EXPRESSION = decl.expr
                    package._pt_attach_constant(decl.name, constant)
                    # Check for a constant override
                    if decl.name in constant_overrides:
                        get_log().debug(
                            f"Overriding constant '{decl.name}' with value "
                            f"{constant_overrides[decl.name]}"
                        )
                        constant._pt_set(int(constant_overrides[decl.name]))
                    # Remember this constant
                    known_entities[decl.name] = (constant, decl.position)
                # Build instances (constants that reference other types)
                case DeclInstance():
                    # Check for name collisions
                    _check_collision(decl.name)
                    # Attach to the package
                    package._pt_attach_instance(
                        decl.name,
                        inst := decl.to_instance(_resolve),
                    )
                    # Remember this type
                    known_entities[decl.name] = (inst, decl.position)
                # Build aliases and scalars
                case DeclScalar() | DeclAlias():
                    # Check for name collisions
                    _check_collision(decl.name)
                    # Attach to the package
                    package._pt_attach(
                        obj := decl.to_class(_resolve),
                        name=decl.name,
                    )
                    # Remember this type
                    known_entities[decl.name] = (obj, decl.position)
                # Build enums, structs, and unions
                case DeclEnum() | DeclStruct() | DeclUnion():
                    # Check for name collisions
                    _check_collision(decl.name)
                    # Attach to the package
                    package._pt_attach(obj := decl.to_class(source, _resolve))
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

        # Register with namespace
        namespaces[package.__name__] = package

        # Yield the package
        yield package


def parse(
    path: Path,
    namespaces: dict[str, Package] | None = None,
    constant_overrides: dict[str, int] | None = None,
    keep_expression: bool = False,
) -> Iterable[Package]:
    """
    Parse a Packtype definition from a file path producing a Package object.

    :param path:               The path to the Packtype definition file.
    :param namespaces:         A dictionary of known packages to resolve imports.
    :param constant_overrides: Optional overrides for constants defined within
                               the package, where the key must precisely match
                               the constant's name.
    :param keep_expression:    If True, expressions will be attached to constants
                               allowing them to be re-evaluated with new inputs.
    :yields:                   Package objects representing the parsed definition.
    """
    with path.open("r", encoding="utf-8") as fh:
        yield from parse_string(
            definition=fh.read(),
            namespaces=namespaces,
            constant_overrides=constant_overrides,
            source=path,
            keep_expression=keep_expression,
        )
