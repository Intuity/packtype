# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Iterable

from ..types.base import Base
from ..types.scalar import Scalar
from ..types.union import Union
from .basic import get_name


def _normalise_union(union: Union | type[Union]) -> Union:
    assert isinstance(union, Union) or issubclass(union, Union)
    if not isinstance(union, Union):
        union = union()
    return union


def is_union(ptype: type[Base] | Base) -> bool:
    """
    Check if a Packtype definition is a union.
    :param ptype: The Packtype definition to check
    :return: True if the definition is a union, False otherwise
    """
    return isinstance(ptype, Union) or issubclass(ptype, Union)


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
    return isinstance(member, Scalar) and not member._PT_ATTACHED_TO


def get_member_type(member: Base) -> str | None:
    """
    Get the type name of a member in a Packtype union.
    :param member: The member to inspect
    :return: The type name of the member if it is not a simple member, else None
    """
    return None if is_simple_member(member) else get_name(member)
