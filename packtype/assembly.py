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

import functools
from enum import Enum, auto
from typing import Any

from .array import Array, ArraySpec
from .base import Base
from .primitive import Primitive


class Packing(Enum):
    FROM_LSB = auto()
    FROM_MSB = auto()


class WidthError(Exception):
    pass


class Assembly(Base):
    def __init__(self, parent: Base | None = None) -> None:
        super().__init__(parent)
        self._pt_fields = {}
        for fname, ftype, fval in self._pt_definitions:
            if isinstance(ftype, ArraySpec):
                if isinstance(ftype.base, Primitive):
                    finst = Array(ftype, parent=self, default=fval)
                else:
                    finst = Array(ftype, parent=self)
            elif issubclass(ftype, Primitive):
                finst = ftype(parent=self, default=fval)
            else:
                finst = ftype(parent=self)
            setattr(self, fname, finst)
            self._pt_fields[finst] = fname

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name) and isinstance(obj := getattr(self, name), Base):
            obj._pt_set(value)
        else:
            return super().__setattr__(name, value)

    def _pt_lookup(self, field: type[Base] | Base) -> str:
        return self._pt_fields[field]


class PackedAssembly(Assembly):
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {
        "packing": (Packing.FROM_LSB, [Packing.FROM_LSB, Packing.FROM_MSB]),
        "width": (-1, lambda x: int(x) > 0),
    }

    def __init__(self, parent: Base | None = None) -> None:
        super().__init__(parent)
        self._pt_packing = self._PT_ATTRIBUTES["packing"]
        self._pt_width = int(self._PT_ATTRIBUTES["width"])
        self._pt_ranges = {}
        # Check for oversized fields
        if self._pt_width < 0:
            self._pt_width = self._pt_field_width
        elif self._pt_width < self._pt_field_width:
            raise WidthError(
                f"Fields of {type(self).__name__} total {self._pt_field_width} "
                f"bits which does not fit within the specified width of "
                f"{self._pt_width} bits"
            )
        # Place fields LSB -> MSB
        if self._pt_packing is Packing.FROM_LSB:
            lsb = 0
            for finst, fname in self._pt_fields.items():
                if isinstance(finst, Array):
                    for idx, entry in enumerate(finst):
                        self._pt_ranges[fname, idx] = (lsb, lsb + entry._pt_width - 1)
                        lsb += entry._pt_width
                else:
                    self._pt_ranges[fname] = (lsb, lsb + finst._pt_width - 1)
                    lsb += finst._pt_width
        # Place fields MSB -> LSB
        else:
            msb = self._pt_width - 1
            for finst, fname in self._pt_fields.items():
                if isinstance(finst, Array):
                    for idx, entry in enumerate(finst):
                        self._pt_ranges[fname, idx] = (msb - entry._pt_width + 1, msb)
                        msb -= entry._pt_width
                else:
                    self._pt_ranges[fname] = (msb - finst._pt_width + 1, msb)
                    msb -= finst._pt_width

    @property
    @functools.cache  # noqa: B019
    def _pt_field_width(self) -> None:
        total_width = 0
        for field in self._pt_fields.keys():
            if isinstance(field, Array):
                total_width += sum(x._pt_width for x in field)
            else:
                total_width += field._pt_width
        return total_width

    @property
    def _pt_mask(self) -> None:
        return (1 << self._pt_width) - 1

    @property
    def _pt_fields_lsb_asc(self) -> list[Base]:
        pairs = []
        for finst, fname in self._pt_fields.items():
            key = (fname, 0) if isinstance(finst, Array) else fname
            lsb, msb = self._pt_ranges[key]
            pairs.append((lsb, msb, (fname, finst)))
        return sorted(pairs, key=lambda x: x[0])

    @property
    def _pt_fields_msb_desc(self) -> list[Base]:
        pairs = []
        for finst, fname in self._pt_fields.items():
            key = (fname, 0) if isinstance(finst, Array) else fname
            lsb, msb = self._pt_ranges[key]
            pairs.append((lsb, msb, (fname, finst)))
        return sorted(pairs, key=lambda x: x[1], reverse=True)

    def _pt_lsb(self, field: str) -> int:
        return self._pt_ranges[field][0]

    def _pt_msb(self, field: str) -> int:
        return self._pt_ranges[field][1]

    def _pt_pack(self) -> int:
        packed = 0
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, Array):
                for idx, entry in enumerate(finst):
                    packed |= (int(entry) & entry._pt_mask) << self._pt_lsb(
                        (fname, idx)
                    )
            else:
                packed |= (int(finst) & finst._pt_mask) << self._pt_lsb(fname)
        return packed

    @classmethod
    def _pt_unpack(cls, packed: int) -> "PackedAssembly":
        inst = cls()
        inst._pt_set(packed)
        return inst

    def __int__(self) -> int:
        return self._pt_pack()

    def _pt_set(self, value: int) -> None:
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, Array):
                for idx, entry in enumerate(finst):
                    entry._pt_set(
                        (value >> self._pt_lsb((fname, idx))) & entry._pt_mask
                    )
            else:
                finst._pt_set((value >> self._pt_lsb(fname)) & finst._pt_mask)
