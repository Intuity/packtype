# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from typing import Any

from ..types.array import PackedArray, UnpackedArray


def is_packed_array(ptype: Any) -> bool:
    """
    Determine if a field is a packed array instance.
    :param ptype: The field to check
    :return: True if the field is a packed array instance, False otherwise
    """
    return isinstance(ptype, PackedArray)

