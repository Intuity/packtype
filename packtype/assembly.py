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
import math
from typing import Any

from .array import ArraySpec, PackedArray
from .base import Base
from .bitvector import BitVector, BitVectorWindow
from .numeric import Numeric
from .packing import Packing
from .primitive import NumericPrimitive
from .scalar import Scalar


class WidthError(Exception):
    pass


class AssignmentError(Exception):
    pass


class Assembly(Base, Numeric):
    def __init__(self, _pt_bv: BitVector | BitVectorWindow | None = None) -> None:
        self._pt_fields = {}
        super().__init__(_pt_bv=_pt_bv)

    def __setattr__(self, name: str, value: Any) -> None:
        try:
            return getattr(self, name)._pt_set(value)
        except AttributeError:
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

    def __init__(
        self, _pt_bv: BitVector | BitVectorWindow | None = None, **kwds
    ) -> None:
        super().__init__(_pt_bv=BitVector(self._PT_WIDTH) if _pt_bv is None else _pt_bv)
        for fname, ftype, fval in self._pt_definitions():
            lsb, msb = self._PT_RANGES[fname]
            if isinstance(ftype, ArraySpec):
                if isinstance(ftype.base, NumericPrimitive):
                    finst = ftype.as_packed(
                        default=fval,
                        packing=self._PT_PACKING,
                        _pt_bv=self._pt_bv.create_window(msb, lsb),
                    )
                else:
                    finst = ftype.as_packed(
                        packing=self._PT_PACKING,
                        _pt_bv=self._pt_bv.create_window(msb, lsb),
                    )
            elif issubclass(ftype, NumericPrimitive):
                finst = ftype(default=fval, _pt_bv=self._pt_bv.create_window(msb, lsb))
            else:
                finst = ftype(_pt_bv=self._pt_bv.create_window(msb, lsb))
            finst._PT_PARENT = self
            setattr(self, fname, finst)
            self._pt_fields[finst] = fname
            # If a value was provided, assign it
            if (fval := kwds.get(fname, None)) is not None:
                if isinstance(finst, PackedArray):
                    if not isinstance(fval, list) or len(fval) != len(finst):
                        raise AssignmentError(
                            f"Cannot assign value to field {fname} as it is an array "
                            f"of {len(finst)} entries and the assigned value does "
                            f"not have the same dimensions"
                        )
                    for sub_val, sub_field in zip(fval, finst, strict=False):
                        sub_field._pt_set(sub_val)
                else:
                    finst._pt_set(fval)
                # Delete from kwds to track
                del kwds[fname]
        # Flag any unused field values
        if kwds:
            raise AssignmentError(
                f"{type(self).__name__} does not contain fields called "
                + ", ".join(f"'{x}'" for x in kwds.keys())
            )
        # Create padding field
        if self._PT_PADDING > 0:
            padding = Scalar[self._PT_PADDING](_pt_bv=self._pt_bv)
            self._padding = padding
            self._pt_fields[padding] = "_padding"

    def __str__(self) -> str:
        lines = [
            f"{type(self).__name__} - width: {self._PT_WIDTH}, raw: 0x{int(self):X}"
        ]
        max_bits = int(math.ceil(math.log(self._PT_WIDTH, 10)))
        max_name = max(map(len, self._pt_fields.values()))
        for finst, fname in self._pt_fields.items():
            lsb, msb = self._PT_RANGES[fname]
            lines.append(
                f" - [{msb:{max_bits}}:{lsb:{max_bits}}] {fname:{max_name}} "
                f"= 0x{int(finst):X}"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self.__str__()

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
                # For arrays record each component placement separately
                if isinstance(ftype, ArraySpec):
                    fwidth = ftype.base()._pt_width
                    part_lsb = lsb
                    for idx in range(ftype.dimension):
                        cls._PT_RANGES[fname, idx] = (part_lsb, part_lsb + fwidth - 1)
                        part_lsb += fwidth
                # For every field type (including arrays) record full placement
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
                # For arrays record each component placement separately
                if isinstance(ftype, ArraySpec):
                    fwidth = ftype.base()._pt_width
                    part_msb = msb
                    for idx in range(ftype.dimension):
                        cls._PT_RANGES[fname, idx] = (part_msb - fwidth + 1, part_msb)
                        part_msb -= fwidth
                # For every field type (including arrays) record full placement
                fwidth = ftype()._pt_width
                cls._PT_RANGES[fname] = (msb - fwidth + 1, msb)
                msb -= fwidth
            # Insert padding
            cls._PT_PADDING = max(0, msb + 1)
            if cls._PT_PADDING > 0:
                cls._PT_RANGES["_padding"] = (0, msb)

    @classmethod
    @functools.cache
    def _pt_field_width(cls) -> int:
        total_width = 0
        for _, ftype, _ in cls._pt_definitions():
            total_width += ftype()._pt_width
        return total_width

    @property
    def _pt_width(self) -> int:
        return self._PT_WIDTH

    @property
    @functools.cache
    def _pt_mask(self) -> int:
        return (1 << self._PT_WIDTH) - 1

    @property
    @functools.cache
    def _pt_fields_lsb_asc(self) -> list[Base]:
        pairs = []
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, PackedArray):
                lsb = min(self._PT_RANGES[(fname, x)][0] for x in range(len(finst)))
                msb = max(self._PT_RANGES[(fname, x)][1] for x in range(len(finst)))
            else:
                lsb, msb = self._PT_RANGES[fname]
            pairs.append((lsb, msb, (fname, finst)))
        return sorted(pairs, key=lambda x: x[0])

    @property
    @functools.cache
    def _pt_fields_msb_desc(self) -> list[Base]:
        pairs = []
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, PackedArray):
                lsb = min(self._PT_RANGES[(fname, x)][0] for x in range(len(finst)))
                msb = max(self._PT_RANGES[(fname, x)][1] for x in range(len(finst)))
            else:
                lsb, msb = self._PT_RANGES[fname]
            pairs.append((lsb, msb, (fname, finst)))
        return sorted(pairs, key=lambda x: x[1], reverse=True)

    @functools.cache
    def _pt_lsb(self, field: str) -> int:
        return self._PT_RANGES[field][0]

    @functools.cache
    def _pt_msb(self, field: str) -> int:
        return self._PT_RANGES[field][1]

    def _pt_pack(self) -> int:
        return int(self._pt_bv)

    @classmethod
    def _pt_unpack(cls, packed: int) -> "PackedAssembly":
        inst = cls()
        inst._pt_set(packed)
        return inst

    def __int__(self) -> int:
        return self._pt_pack()

    def _pt_set(self, value: int) -> None:
        self._pt_bv.set(value)
