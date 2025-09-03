# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import inspect
import math

from ..types.alias import Alias
from ..types.assembly import PackedAssembly
from ..types.base import Base
from ..types.enum import Enum
from ..types.primitive import NumericType
from ..types.scalar import ScalarType
from ..types.union import Union


def clog2(x: int) -> int:
    """
    Calculate the ceiling of the base-2 logarithm of x.
    :param x: The integer to calculate the logarithm of
    :return: The ceiling of the base-2 logarithm of x
    """
    assert x > 0, "Input must be a positive integer."
    return math.ceil(math.log2(x))


def get_width(
    ptype: type[PackedAssembly | Enum | NumericType | Union] | PackedAssembly | NumericType | Union,
) -> int:
    """
    Get the width of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The width in bits of the Packtype definition
    """
    if isinstance(ptype, PackedAssembly | Enum | NumericType | Union):
        return ptype._pt_width
    elif issubclass(ptype, PackedAssembly | Enum | NumericType | Union):
        return ptype._PT_WIDTH
    elif issubclass(ptype, Alias):
        return get_width(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_name(ptype: type[Base] | Base) -> str:
    """
    Get the name of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The name of the Packtype definition
    """
    if isinstance(ptype, ScalarType) or (inspect.isclass(ptype) and issubclass(ptype, ScalarType)):
        ptype = ptype if inspect.isclass(ptype) else type(ptype)
        return ptype._PT_ATTACHED_TO._PT_FIELDS[ptype]
    elif isinstance(ptype, Base) or (inspect.isclass(ptype) and issubclass(ptype, Base)):
        return ptype._pt_name()
    elif issubclass(ptype, Alias):
        return get_name(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_package(ptype: type[Base] | Base) -> type[Base] | None:
    """
    Get the package a Packtype definition is attached to, if the type is not
    associated to a package then None will be returned
    :param ptype: The Packtype definition to inspect
    :return: The Package to which this type is attached
    """
    if not isinstance(ptype, Base) and not (inspect.isclass(ptype) and issubclass(ptype, Base)):
        raise TypeError(f"{ptype} is not a Packtype definition")
    return ptype._PT_ATTACHED_TO


def get_doc(ptype: type[Base] | Base) -> str:
    """
    Get the docstring of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The docstring of the Packtype definition
    """
    if isinstance(ptype, Base) or issubclass(ptype, Base):
        return ptype.__doc__ or ""
    elif issubclass(ptype, Alias):
        return get_doc(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_source(ptype: type[Base] | Base) -> tuple[str, int]:
    """
    Get the name of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The source file and line number of the Packtype definition
    """
    if isinstance(ptype, Base) or issubclass(ptype, Base):
        return ptype._PT_SOURCE
    elif issubclass(ptype, Alias):
        return get_source(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def is_signed(ptype: type[NumericType] | NumericType) -> bool:
    """
    Check if a Packtype definition is signed
    :param ptype: The Packtype definition to check
    :return: True if the definition is signed, False otherwise
    """
    if isinstance(ptype, NumericType):
        return ptype._pt_signed
    elif issubclass(ptype, NumericType):
        return ptype._PT_SIGNED
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def unpack(ptype: type[Base], value: int) -> Base:
    """
    Unpack a value into a Packtype definition
    :param ptype: The Packtype definition to unpack into
    :param value: The value to unpack
    :return: An instance of the Packtype definition with the unpacked value
    """
    if not inspect.isclass(ptype):
        raise TypeError(f"{ptype} is an instance of a Packtype definition")
    if not issubclass(ptype, Base):
        raise TypeError(f"{ptype} is not a Packtype definition")
    if issubclass(ptype, NumericType):
        return ptype(value)
    elif issubclass(ptype, Enum):
        return ptype._pt_cast(value)
    else:
        return ptype._pt_unpack(value)


def pack(pinst: Base) -> int:
    """
    Pack an instance of a Packtype definition into an integer
    :param pinst: The instance of the Packtype definition to pack
    :return: The packed value as an integer
    """
    if inspect.isclass(pinst):
        raise TypeError(f"{pinst} is not an instance of a Packtype definition")
    return int(pinst)


def is_scalar(ptype: type[Base] | Base) -> bool:
    """
    Check if a Packtype definition is a scalar type
    :param ptype: The Packtype definition to check
    :return: True if the definition is a scalar type, False otherwise
    """
    return isinstance(ptype, ScalarType) or (
        inspect.isclass(ptype) and issubclass(ptype, ScalarType)
    )
