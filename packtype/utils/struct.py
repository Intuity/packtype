# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from ..types.base import Base
from ..types.scalar import ScalarType
from ..types.struct import Struct
from .basic import get_name


def _normalise_struct(struct: Struct | type[Struct]) -> Struct:
    assert isinstance(struct, Struct) or issubclass(struct, Struct)
    if not isinstance(struct, Struct):
        struct = struct()
    return struct


def is_struct(ptype: type[Base] | Base) -> bool:
    """
    Check if a Packtype definition is a struct.
    :param ptype: The Packtype definition to check
    :return: True if the definition is a struct, False otherwise
    """
    return isinstance(ptype, Struct) or issubclass(ptype, Struct)


def get_fields_msb_desc(struct: Struct | type[Struct]) -> list[tuple[int, int, tuple[str, Base]]]:
    """
    Get the fields of a Packtype struct in MSB-first order.
    :param struct: The Packtype struct to inspect
    :return: List of tuples of LSB, MSB, and inner tuple of field name and type
    """
    struct = _normalise_struct(struct)
    return struct._pt_fields_msb_desc


def get_fields_lsb_asc(struct: Struct | type[Struct]) -> list[tuple[int, int, tuple[str, Base]]]:
    """
    Get the fields of a Packtype struct in LSB-first order.
    :param struct: The Packtype struct to inspect
    :return: List of tuples of LSB, MSB, and inner tuple of field name and type
    """
    struct = _normalise_struct(struct)
    return struct._pt_fields_lsb_asc


def is_simple_field(field: Base) -> bool:
    """
    Check if a field in a Packtype struct is a simple scalar field and does not
    refer to another existing type
    :param field: The field to check
    :return: True if the field is a simple field, False otherwise
    """
    return isinstance(field, ScalarType) and not field._PT_ATTACHED_TO


def get_field_type(field: Base) -> str | None:
    """
    Get the type name of a field in a Packtype struct.
    :param field: The field to inspect
    :return: The type name of the field if it is not a simple field, else None
    """
    return None if is_simple_field(field) else get_name(field)
