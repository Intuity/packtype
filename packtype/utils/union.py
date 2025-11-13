# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import inspect
from collections.abc import Iterable

from ..types.base import Base
from ..types.scalar import ScalarType
from ..types.union import Union
from .basic import get_name


def is_union(ptype: type[Base] | Base) -> bool:
    """
    Check if a Packtype definition is a union.
    :param ptype: The Packtype definition to check
    :return: True if the definition is a union, False otherwise
    """
    return isinstance(ptype, Union) or (inspect.isclass(ptype) and issubclass(ptype, Union))


def _normalise_union(inst_or_type: Union | type[Union]) -> Union:
    """
    Utility functions may be called with a type instance or the type definition,
    and certain operations require an instance. This function ensures that the
    input is 'normalised' to be an instance.

    :param union: The union instance or union type definition
    :return: A union instance
    """
    assert is_union(inst_or_type), "Input must be a Union or subclass thereof."
    return inst_or_type if isinstance(inst_or_type, Union) else inst_or_type()


def get_members(union: Union | type[Union]) -> Iterable[tuple[str, Base]]:
    """
    Get the members of a Packtype union
    :param union: The Packtype union to inspect
    :return: List of tuples of member name and type
    """
    union = _normalise_union(union)
    for finst, fname in union._pt_fields.items():
        yield fname, finst


def is_simple_member(member: Base) -> bool:
    """
    Check if a member in a Packtype union is a simple scalar member and does not
    refer to another existing type
    :param member: The member to check
    :return: True if the member is a simple member, False otherwise
    """
    return isinstance(member, ScalarType) and not member._PT_ATTACHED_TO


def get_member_type(member: Base) -> str | None:
    """
    Get the type name of a member in a Packtype union.
    :param member: The member to inspect
    :return: The type name of the member if it is not a simple member, else None
    """
    return None if is_simple_member(member) else get_name(member)
