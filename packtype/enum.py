# Copyright 2023, Peter Birch, mailto:peter@intuity.io
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

import enum
import math
from typing import Any

from .assembly import Assembly
from .base import Base


class EnumMode(enum.Enum):
    INDEXED = enum.auto()
    ONE_HOT = enum.auto()
    GRAY = enum.auto()


class EnumError(Exception):
    pass


class Enum(Assembly):
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {
        "mode": (EnumMode.INDEXED, list(EnumMode)),
        "width": (-1, lambda x: int(x) > 0),
        "prefix": (None, lambda x: isinstance(x, str)),
    }

    def __init__(self, parent: Base | None = None) -> None:
        super().__init__(parent)
        self._pt_mode = self._PT_ATTRIBUTES["mode"]
        self._pt_width = self._PT_ATTRIBUTES["width"]
        self._pt_prefix = self._PT_ATTRIBUTES["prefix"]
        if self._pt_prefix is None:
            self._pt_prefix = self._pt_name()
        self._pt_lookup = {}
        # Indexed
        if self._pt_mode is EnumMode.INDEXED:
            next_val = 0
            for _, fval in self._pt_fields:
                if fval.value is None:
                    fval.value = next_val
                next_val = fval.value + 1
        # One-hot
        elif self._pt_mode is EnumMode.ONE_HOT:
            next_val = 1
            for fname, fval in self._pt_fields:
                if fval.value is None:
                    fval.value = next_val
                if (math.log2(fval.value) % 1) != 0:
                    raise EnumError(
                        f"Enum entry {fname} has value {fval.value} that is not "
                        f"one-hot"
                    )
                next_val = (fval.value << 1)
        # Gray code
        elif self._pt_mode is EnumMode.GRAY:
            for idx, (fname, fval) in enumerate(self._pt_fields):
                gray_val = (idx ^ (idx >> 1))
                if fval.value is None:
                    fval.value = gray_val
                elif fval.value != gray_val:
                    raise EnumError(
                        f"Enum entry {fname} has value {fval.value} that does "
                        f"not conform to the expected Gray code value of {gray_val}"
                    )
        # Determine width
        if self._pt_width < 0:
            self._pt_width = int(math.ceil(math.log2(
                max(x[1].value for x in self._pt_fields)+1)
            ))
        # Final checks
        used = []
        max_val = (1 << self._pt_width) - 1
        for fname, fval in self._pt_fields:
            # Check for oversized values
            if fval.value > max_val:
                raise EnumError(
                    f"Enum entry {fname} has value {fval.value} that cannot be "
                    f"encoded in a bit width of {self._pt_width}"
                )
            # Check for repeated values
            if fval.value in used:
                raise EnumError(
                    f"Enum entry {fname} has value {fval.value} that appears "
                    f"more than once in the enumeration"
                )
            used.append(fval.value)
            # Create a lookup table
            self._pt_lookup[fval.value] = (fname, fval)
