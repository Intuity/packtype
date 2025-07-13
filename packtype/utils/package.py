# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Iterable

from ..types.constant import Constant
from ..types.enum import Enum
from ..types.package import Package
from ..types.scalar import Scalar
from ..types.struct import Struct
from ..types.union import Union
from .basic import get_name


def _normalise_package(pkg: Package | type[Package]) -> Package:
    assert isinstance(pkg, Package) or issubclass(pkg, Package)
    if not isinstance(pkg, Package):
        pkg = pkg()
    return pkg


def get_imports(pkg: Package | type[Package]) -> Iterable[tuple[str, str]]:
    """
    List the imports of a Packtype package.
    :return: Iterable of tuples of the foreign package name and the imported object's name
    """
    pkg = _normalise_package(pkg)
    for foreign in pkg._pt_foreign():
        if foreign._PT_ATTACHED_TO:
            foreign_name = foreign._PT_ATTACHED_TO._pt_lookup(foreign)
        else:
            foreign_name = get_name(foreign)
        yield (get_name(foreign._PT_ATTACHED_TO), foreign_name)


def get_constants(pkg: Package | type[Package]) -> Iterable[tuple[str, Constant]]:
    """
    Get the constants defined in a Packtype package.
    :return: Iterable of tuples of the constant name and definition
    """
    pkg = _normalise_package(pkg)
    return pkg._pt_constants


def get_scalars(pkg: Package | type[Package]) -> Iterable[tuple[str, type[Scalar]]]:
    """
    Get the scalars defined in a Packtype package.
    :return: Iterable of tuples of the scalar name and definition
    """
    pkg = _normalise_package(pkg)
    return pkg._pt_scalars


def get_enums(pkg: Package | type[Package]) -> Iterable[tuple[str, type[Enum]]]:
    """
    Get the enums defined in a Packtype package.
    :return: Iterable of tuples of the enum name and definition
    """
    pkg = _normalise_package(pkg)
    return pkg._pt_enums


def get_structs_and_unions(
    pkg: Package | type[Package],
) -> Iterable[tuple[str, type[Struct | Union]]]:
    """
    Get the structs and unions defined in a Packtype package.
    :return: Iterable of tuples of the struct/union name and definition
    """
    pkg = _normalise_package(pkg)
    return pkg._pt_structs_and_unions
