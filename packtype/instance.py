# Copyright 2024, Peter Birch, mailto:peter@intuity.io
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

import math
from typing import Any

from .assembly import Assembly
from .bitvector import BitVector, BitVectorWindow


class Instance:
    """
    Provides a wrapper around an assembly definition and a bitvector and forms
    projections onto the data.

    :param assembly:  Definition of the assembly
    :param bitvector: Bitvector carrying the instance's data
    """

    def __init__(self,
                 assembly: Assembly,
                 bitvector: BitVector | BitVectorWindow) -> None:
        self._pt_assembly = assembly
        self._pt_bitvector = bitvector

    def __getattr__(self, key: str) -> Any:
        try:
            obj = getattr(self._pt_assembly, key)
            lsb, msb = self._pt_assembly._PT_RANGES[key]
            window = self._pt_bitvector.create_window(msb, lsb)
            if isinstance(obj, Assembly):
                return Instance(obj, window)
            else:
                return window
        except AttributeError:
            return getattr(super(), key)

    def __str__(self) -> str:
        lines = [
            f"{type(self._pt_assembly).__name__} - "
            f"width: {self._pt_assembly._PT_WIDTH}, "
            f"raw: 0x{int(self._pt_bitvector):X}"
        ]
        max_bits = int(math.ceil(math.log(self._pt_assembly._PT_WIDTH, 10)))
        max_name = max(map(len, self._pt_assembly._pt_fields.values()))
        for fname in self._pt_assembly._pt_fields.values():
            lsb, msb = self._pt_assembly._PT_RANGES[fname]
            lines.append(
                f" - [{msb:{max_bits}}:{lsb:{max_bits}}] {fname:{max_name}} "
                f"= 0x{int(self._pt_bitvector.create_window(msb, lsb)):X}"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self.__str__()
