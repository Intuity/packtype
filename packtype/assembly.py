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

import dataclasses
import functools
from enum import Enum, auto
from typing import Any

from .base import Base
from .primitive import Primitive


class Packing(Enum):
    FROM_LSB = auto()
    FROM_MSB = auto()


class WidthError(Exception):
    pass


class Assembly(Base):
    _PT_DEF = None
    _PT_ATTACH = None

    def __init__(self) -> None:
        self._pt_fields = []
        for fname, ftype, fval in self._pt_definitions:
            if issubclass(ftype, Primitive):
                finst = ftype(default=fval)
            else:
                finst = ftype()
            setattr(self, fname, finst)
            self._pt_fields.append((fname, finst))
        for attach in self._PT_ATTACH:
            setattr(self, attach.__name__, attach)

    @property
    def _pt_definitions(self) -> list[str, Any]:
        yield from ((x.name, x.type, x.default) for x in dataclasses.fields(self._PT_DEF))

    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, name) and isinstance(obj := getattr(self, name), Base):
            obj._pt_set(value)
        else:
            return super().__setattr__(name, value)


class PackedAssembly(Assembly):
    _PT_ATTRIBUTES: dict[str, Any] = {
        "packing": (Packing.FROM_LSB, [Packing.FROM_LSB, Packing.FROM_MSB]),
        "width": (-1, lambda x: x > 0),
    }

    def __init__(self) -> None:
        super().__init__()
        self._pt_packing = self._PT_ATTRIBUTES["packing"]
        self._pt_width = self._PT_ATTRIBUTES["width"]
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
            for fname, finst in self._pt_fields:
                self._pt_ranges[fname] = (lsb, lsb+finst._pt_width-1)
                lsb += finst._pt_width
        # Place fields MSB -> LSB
        else:
            msb = self._pt_width - 1
            for fname, finst in self._pt_fields:
                self._pt_ranges[fname] = (msb-finst._pt_width+1, msb)
                msb -= finst._pt_width

    @property
    @functools.cache
    def _pt_field_width(self) -> None:
        return sum(x._pt_width for _, x in self._pt_fields)

    @property
    def _pt_mask(self) -> None:
        return (1 << self._pt_width) - 1

    def _pt_lsb(self, field: str) -> int:
        return self._pt_ranges[field][0]

    def _pt_msb(self, field: str) -> int:
        return self._pt_ranges[field][1]

    def _pt_pack(self) -> int:
        packed = 0
        for fname, field in self._pt_fields:
            packed |= (int(field) & field._pt_mask) << self._pt_lsb(fname)
        return packed

    @classmethod
    def _pt_unpack(cls, packed: int) -> "PackedAssembly":
        inst = cls()
        for fname, field in inst._pt_fields:
            field._pt_set((packed >> inst._pt_lsb(fname)) & field._pt_mask)
        return inst

    def __int__(self) -> int:
        return self._pt_pack()
