# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Iterable

from ..types.enum import Enum
from ..types.package import Package


def _normalise_enum(enum: Enum | type[Enum]) -> Package:
    assert isinstance(enum, Enum) or issubclass(enum, Enum)
    if not isinstance(enum, Enum):
        enum = enum()
    return enum


def get_entries(enum: Enum | type[Enum]) -> Iterable[tuple[str, int, bool]]:
    """
    Iterate the entries of a Packtype enum.
    :param enum: The Packtype enum to inspect
    :yield: Tuple of the enum name, value, and whether it is the last entry
    """
    enum = _normalise_enum(enum)
    for idx, (v_name, v_val) in enumerate(enum._pt_as_dict().items()):
        yield v_name, int(v_val), idx == (len(enum._PT_LKP_INST) - 1)
