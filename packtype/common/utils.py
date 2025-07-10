# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math
from collections.abc import Iterable

from ..types.alias import Alias
from ..types.assembly import PackedAssembly
from ..types.base import Base
from ..types.constant import Constant
from ..types.enum import Enum
from ..types.package import Package
from ..types.primitive import NumericPrimitive
from ..types.union import Union


def clog2(x: int) -> int:
    """Calculate the ceiling of the base-2 logarithm of x."""
    assert x > 0, "Input must be a positive integer."
    return math.ceil(math.log2(x))


def width(
    ptype: type[PackedAssembly | Enum | NumericPrimitive | Union]
    | PackedAssembly
    | NumericPrimitive
    | Union,
) -> int:
    """Get the width of a Packtype definition"""
    if isinstance(ptype, PackedAssembly | Enum | NumericPrimitive | Union):
        return ptype._pt_width
    elif issubclass(ptype, PackedAssembly | Enum | NumericPrimitive | Union):
        return ptype._PT_WIDTH
    elif issubclass(ptype, Alias):
        return width(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def name(ptype: type[Base] | Base) -> str:
    """Get the name of a Packtype definition"""
    if isinstance(ptype, Base) or issubclass(ptype, Base):
        return ptype._pt_name()
    elif issubclass(ptype, Alias):
        return name(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_source(ptype: type[Base] | Base) -> str:
    """Get the name of a Packtype definition"""
    if isinstance(ptype, Base) or issubclass(ptype, Base):
        return ptype._PT_SOURCE
    elif issubclass(ptype, Alias):
        return name(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def is_signed(ptype: type[NumericPrimitive] | NumericPrimitive) -> bool:
    """Check if a Packtype definition is signed"""
    if isinstance(ptype, NumericPrimitive):
        return ptype._pt_signed
    elif issubclass(ptype, NumericPrimitive):
        return ptype._PT_SIGNED
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_package_constants(pkg: Package) -> Iterable[tuple[str, Constant]]:
    return pkg._pt_constants
