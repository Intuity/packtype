# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
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
from typing import Any, Iterable

from .array import ArraySpec, PackedArray
from .base import Base
from .bitvector import BitVector, BitVectorWindow
from .constant import Constant
from .numeric import Numeric
from .packing import Packing
from .scalar import Scalar
from .svg.render import ElementStyle, SvgConfig, SvgField, SvgRender

class WidthError(Exception):
    pass


class AssignmentError(Exception):
    pass


class Assembly(Base, Numeric):
    _PT_ALLOW_DEFAULTS: list[type[Base]] = [Constant]

    def __init__(self, _pt_bv: BitVector | BitVectorWindow | None = None, default: int | None = None):
        super().__init__(_pt_bv=_pt_bv, default=default)

    def _pt_force_set(self, name: str, value: Any):
        super().__setattr__(name, value)

    def __setattr__(self, name: str, value: Any):
        if name in self._PT_DEF.keys():
            getattr(self, name)._pt_set(value)
        else:
            return super().__setattr__(name, value)

    def _pt_lookup(self, field: type[Base] | Base) -> str:
        return self._pt_fields[field]

    @property
    @functools.lru_cache()
    def _pt_fields(self) -> dict:
        return { getattr(self, x): x for x in self._PT_DEF.keys() }


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
        self,
        _pt_bv: BitVector | BitVectorWindow | None = None,
        default: int | None = None,
        **kwds,
    ):
        super().__init__(_pt_bv=BitVector(self._PT_WIDTH) if _pt_bv is None else _pt_bv, default=default)
        # Attempt to assign keyword values to fields
        for fname, fval in kwds.items():
            try:
                finst = getattr(self, fname)
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
            except AttributeError as e:
                raise AssignmentError(
                    f"{type(self).__name__} does not contain a field called '{fname}'"
                ) from e

    @property
    @functools.lru_cache()
    def _pt_fields(self) -> dict:
        base = super()._pt_fields
        if self._PT_PADDING > 0:
            base.update({ self._padding: "_padding" })
        return base

    def __getattribute__(self, fname: str):
        # Attempt to resolve the attribute from existing properties
        try:
            return super().__getattribute__(fname)
        # If that fails...
        except AttributeError as e:
            # Is this a known field that hasn't yet been instanced?
            if fpair := type(self)._PT_DEF.get(fname, None):
                ftype, fval = fpair
                lsb, msb = self._PT_RANGES[fname]
                window = self._pt_bv.create_window(msb, lsb)
                if isinstance(ftype, ArraySpec):
                    finst = ftype.as_packed(packing=self._PT_PACKING, _pt_bv=window)
                else:
                    finst = ftype(_pt_bv=window)
                finst._PT_PARENT = self
                self._pt_force_set(fname, finst)
                # If a value was provided, assign it
                if fval is not None:
                    finst._pt_set(fval)
                # Return it
                return finst
            # Is this the padding field?
            elif fname == "_padding" and self._PT_PADDING > 0:
                padding = Scalar[self._PT_PADDING](_pt_bv=self._pt_bv)
                self._pt_force_set("_padding", padding)
                return padding
            # If not resolved, forward the attribute error
            else:
                raise e

    def __str__(self) -> str:
        lines = [
            f"{type(self).__name__}: 0x{int(self):X}"
        ]
        max_bits = int(math.ceil(math.log(self._PT_WIDTH, 10)))
        max_name = max(map(len, self._PT_DEF.keys()))
        for fname in self._PT_DEF.keys():
            finst = getattr(self, fname)
            lsb, msb = self._PT_RANGES[fname]
            lines.append(
                f" - [{msb:{max_bits}}:{lsb:{max_bits}}] {fname:{max_name}} "
                f"= 0x{int(finst):X}"
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self.__str__()

    def _repr_svg_(self) -> str:
        return self._pt_as_svg()

    def _pt_as_svg(self, cfg: SvgConfig | None = None) -> str:
        """
        Return an SVG representation of the packed assembly.

        :param cfg: Optional SvgConfig to use for rendering
        :return: SVG string representation of the packed assembly
        """
        # If no config is provided, create a default one
        if not cfg:
            cfg = SvgConfig()
            cfg.left_annotation.width = cfg.left_annotation.style.estimate(type(self).__name__).width
            cfg.left_annotation.padding = 10

        # Create a rendering instance
        svg = SvgRender(cfg, left_annotation=type(self).__name__)

        for _lsb, msb, (fname, finst) in self._pt_fields_flat():
            svg.attach(
                SvgField(
                    bit_width=finst._pt_width,
                    name="" if fname == "_padding" else fname,
                    msb=msb,
                    style=ElementStyle.HATCHED if fname == "_padding" else ElementStyle.NORMAL,
                )
            )

        # Return the SVG
        return svg.render()

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
    def _pt_fields_lsb_asc(self) -> list[tuple[int, int, tuple[str, Base]]]:
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
    def _pt_fields_msb_desc(self) -> list[tuple[int, int, tuple[str, Base]]]:
        pairs = []
        for finst, fname in self._pt_fields.items():
            if isinstance(finst, PackedArray):
                lsb = min(self._PT_RANGES[(fname, x)][0] for x in range(len(finst)))
                msb = max(self._PT_RANGES[(fname, x)][1] for x in range(len(finst)))
            else:
                lsb, msb = self._PT_RANGES[fname]
            pairs.append((lsb, msb, (fname, finst)))
        return sorted(pairs, key=lambda x: x[1], reverse=True)

    def _pt_fields_flat(self, offset: int = 0) -> Iterable[tuple[int, int, tuple[str, Base]]]:
        """
        Flatten nested complex fields into a single list of tuples containing
        the LSB, MSB, and a tuple of the field name and its instance.

        :param offset: Offset to apply to the LSB and MSB values
        :return: List of tuples with (LSB, MSB, (field_name, field_instance))
        """
        for lsb, msb, (fname, finst) in self._pt_fields_msb_desc:
            if isinstance(finst, PackedAssembly):
                yield from finst._pt_fields_flat(offset=offset+lsb)
            else:
                yield (lsb+offset, msb+offset, (fname, finst))

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
