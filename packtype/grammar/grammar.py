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

import functools
from pathlib import Path
from typing import Type

from lark import Lark

from packtype.grammar.transformer import PacktypeTransformer
from packtype import Package
from packtype.base import Base
from packtype.wrap import build_from_fields
from packtype.grammar.declarations import (
    DeclImport,
    DeclAlias,
    DeclConstant,
    DeclScalar,
    DeclEnum,
    DeclStruct,
    DeclUnion,
)


@functools.cache
def create_parser():
    parser = Lark.open(
        Path(__file__).parent / "packtype.lark",
        start="root",
        parser="lalr",
        propagate_positions=True,
    )
    return parser


def parse(path: Path) -> Package:
    # Parse the definition
    with path.open("r", encoding="utf-8") as fh:
        defn = PacktypeTransformer().transform(create_parser().parse(fh.read()))
    # Gather declarations
    local_constants: dict[str, int] = {}
    local_types: dict[str, Type[Base]] = {}

    def _rslv_const(name: str) -> int:
        nonlocal local_constants
        if name in local_constants:
            return local_constants[name]
        raise ValueError(f"Failed to resolve '{name}' to a known constant")

    def _rslv_type(name: str) -> Type[Base]:
        nonlocal local_types
        if name in local_types:
            return local_types[name]
        raise ValueError(f"Failed to resolve '{name}' to a known type")

    # Create placeholder package
    package = build_from_fields(Package, defn.name, {}, {})

    # Run through the declarations
    for decl in defn.declarations:
        match decl:
            # Imports
            case DeclImport():
                print("TODO: Handle import")
            # Aliases
            case DeclAlias():
                print("TODO: Handle alias")
            # Build constants
            case DeclConstant():
                package._pt_attach_constant(
                    decl.type,
                    constant := decl.to_instance(_rslv_const)
                )
                local_constants[decl.type] = int(constant)
            # Build scalars
            case DeclScalar():
                package._pt_attach_scalar(
                    decl.type,
                    scalar := decl.to_class(_rslv_const, _rslv_type),
                )
                local_types[decl.type] = scalar
            # Build enums, structs, and unions
            case DeclEnum() | DeclStruct() | DeclUnion():
                package._pt_attach_field(obj := decl.to_class(_rslv_const, _rslv_type))
                local_types[decl.type] = obj
            case _:
                raise Exception(f"Unhandled declaration: {decl}")

    return package
    breakpoint()

EXAMPLE = Path(__file__).parent / "example.pt"
package = parse(EXAMPLE)

breakpoint()
