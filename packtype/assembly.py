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
from .scalar import Scalar


class Packing(Enum):
    FROM_LSB = auto()
    FROM_MSB = auto()


class WidthError(Exception):
    pass


class AssignmentError(Exception):
    pass


class Assembly(Base):
    def __init__(self) -> None:
        super().__init__()
        self._pt_fields = {}
        for fname, ftype, fval in self._pt_definitions():
            if isinstance(ftype, ArraySpec):
                if isinstance(ftype.base, Primitive):
                    finst = Array(ftype, default=fval)
                else:
                    finst = Array(ftype)
            elif issubclass(ftype, Primitive):
                finst = ftype(default=fval)
            else:
                finst = ftype()
            finst._PT_PARENT = self
            setattr(self, fname, finst)
            self._pt_fields[finst] = fname

    def __setattr__(self, name: str, value: Any) -> None:
        if (
            not name.startswith("_")
            and hasattr(self, name)
            and isinstance(obj := getattr(self, name), Base)
        ):
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
    _PT_PACKING: Packing
    _PT_WIDTH: int
    _PT_RANGES: dict
    _PT_PADDING: int

    def __init__(self, **kwds) -> None:
        super().__init__()
        # Create padding field
        if self._PT_PADDING > 0:
            padding = Scalar[self._PT_PADDING]()
            self._pt_fields[padding] = "_padding"
            setattr(self, "_padding", padding)
        # Assign field values
        for key, value in kwds.items():
            field = getattr(self, key, None)
            if field is None:
                raise AssignmentError(
                    f"{type(self).__name__} does not contain a field called "
                    f"'{key}'"
                )
            if isinstance(field, Array):
                if not isinstance(value, list) or len(value) != len(field):
                    raise AssignmentError(
                        f"Cannot assign value to field {key} as it is an array "
                        f"of {len(field)} entries and the assigned value does "
                        f"not have the same dimensions"
                    )
                for idx, aval in enumerate(value):
                    field[idx]._pt_set(aval)
            else:
                field._pt_set(value)

    @classmethod
    def _pt_construct(cls, parent: Base, packing: Packing, width: int):
        cls._PT_PACKING = packing
        cls._PT_WIDTH = int(width)
        cls._PT_RANGES = {}
        # Check for oversized fields
        if cls._PT_WIDTH < 0:
            cls._PT_WIDTH = cls._pt_field_width()
        elif cls._PT_WIDTH < cls._pt_field_width():
            raise WidthError(
                f"Fields of {cls.__name__} total {cls._pt_field_width()} "
                f"bits which does not fit within the specified width of "
                f"{cls._PT_WIDTH} bits"
            )
        # Place fields LSB -> MSB
        if cls._PT_PACKING is Packing.FROM_LSB:
            lsb = 0
            for fname, ftype, _ in cls._pt_definitions():
                if isinstance(ftype, ArraySpec):
                    fwidth = ftype.base()._pt_width
                    for idx in range(ftype.dimension):
                        cls._PT_RANGES[fname, idx] = (lsb, lsb + fwidth - 1)
                        lsb += fwidth
                else:
                    fwidth = ftype()._pt_width
                    cls._PT_RANGES[fname] = (lsb, lsb + fwidth - 1)
                    lsb += fwidth
            # Insert padding
            cls._PT_PADDING = max(0, cls._PT_WIDTH - lsb)
            if cls._PT_PADDING > 0:
                cls._PT_RANGES["_padding"] = (lsb, cls._PT_WIDTH - 1)
        # Place fields MSB -> LSB
        else:
            msb = cls._PT_WIDTH - 1
            for fname, ftype, _ in cls._pt_definitions():
                if isinstance(ftype, ArraySpec):
                    fwidth = ftype.base()._pt_width
                    for idx in range(ftype.dimension):
                        cls._PT_RANGES[fname, idx] = (msb - fwidth + 1, msb)
                        msb -= fwidth
                else:
                    fwidth = ftype()._pt_width
                    cls._PT_RANGES[fname] = (msb - fwidth + 1, msb)
                    msb -= fwidth
            # Insert padding
            cls._PT_PADDING = max(0, msb + 1)
            if cls._PT_PADDING > 0:
                cls._PT_RANGES["_padding"] = (0, msb)

    @classmethod
    @functools.cache  # noqa: B019
    def _pt_field_width(cls) -> int:
        total_width = 0
        for fname, ftype, _ in cls._pt_definitions():
            total_width += ftype()._pt_width
        return total_width

    @property
    def _pt_width(self) -> int:
        return self._PT_WIDTH

    @property
    def _pt_mask(self) -> int:
        return (1 << self._PT_WIDTH) - 1

    @property
    def _pt_fields_lsb_asc(self) -> list[Base]:
        pairs = []
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, Array):
                lsb = min(self._PT_RANGES[(fname, x)][0] for x in range(len(finst)))
                msb = max(self._PT_RANGES[(fname, x)][1] for x in range(len(finst)))
            else:
                lsb, msb = self._PT_RANGES[fname]
            pairs.append((lsb, msb, (fname, finst)))
        return sorted(pairs, key=lambda x: x[0])

    @property
    def _pt_fields_msb_desc(self) -> list[Base]:
        pairs = []
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, Array):
                lsb = min(self._PT_RANGES[(fname, x)][0] for x in range(len(finst)))
                msb = max(self._PT_RANGES[(fname, x)][1] for x in range(len(finst)))
            else:
                lsb, msb = self._PT_RANGES[fname]
            pairs.append((lsb, msb, (fname, finst)))
        return sorted(pairs, key=lambda x: x[1], reverse=True)

    def _pt_lsb(self, field: str) -> int:
        return self._PT_RANGES[field][0]

    def _pt_msb(self, field: str) -> int:
        return self._PT_RANGES[field][1]

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

    def _pt_set(self, value: int, force: bool = False) -> None:
        value = int(value)
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, Array):
                for idx, entry in enumerate(finst):
                    entry._pt_set(
                        (value >> self._pt_lsb((fname, idx))) & entry._pt_mask,
                        force=True,
                    )
            else:
                finst._pt_set(
                    (value >> self._pt_lsb(fname)) & finst._pt_mask, force=True
                )
        if not force:
            self._pt_updated(self)
