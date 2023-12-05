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
from typing import Any

from .assembly import Assembly

class EnumMode(enum.Enum):
    INDEXED = enum.auto()
    ONE_HOT = enum.auto()
    GREY = enum.auto()

class Enum(Assembly):
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {
        "mode": (EnumMode.INDEXED, list(EnumMode)),
    }

    def __init__(self) -> None:
        super().__init__()
        self._pt_mode = self._PT_ATTRIBUTES["mode"]
        next_val = 0
        for fname, fval in self._pt_fields:
            if fval.value is None:
                fval.value = next_val
                next_val += 1
