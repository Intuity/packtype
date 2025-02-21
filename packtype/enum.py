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

import enum
import math
from typing import Any

from .base import Base
from .bitvector import BitVector, BitVectorWindow
from .constant import Constant
from .numeric import Numeric


class EnumMode(enum.Enum):
    INDEXED = enum.auto()
    ONE_HOT = enum.auto()
    GRAY = enum.auto()


class EnumError(Exception):
    pass


class Enum(Base, Numeric):
    _PT_ALLOW_DEFAULTS: list[type[Base]] = [Constant]
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {
        "mode": (EnumMode.INDEXED, list(EnumMode)),
        "width": (-1, lambda x: int(x) > 0),
        "prefix": (None, lambda x: isinstance(x, str)),
    }

    _PT_MODE: EnumMode = EnumMode.INDEXED
    _PT_WIDTH: int
    _PT_PREFIX: str
    _PT_LKP_INST: dict
    _PT_LKP_VALUE: dict

    def __init__(
        self,
        value: int | None = None,
        default: int | None = None,
        _pt_bv: BitVector | BitVectorWindow | None = None,
    ) -> None:
        super().__init__(_pt_bv=_pt_bv, default=default)
        if value is not None:
            self._pt_set(value)
        elif default is not None:
            self._pt_set(default)
        elif _pt_bv is None:
            self._pt_set(0)

    def __repr__(self) -> str:
        name = type(self)._PT_LKP_INST.get(self, "???")
        return f"<Enum::{type(self).__name__} {name}={int(self)}>"

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def _pt_construct(
        cls, parent: Base, mode: EnumMode, width: int, prefix: str | None, **kwds
    ) -> None:
        super()._pt_construct(parent)
        cls._PT_MODE = mode
        cls._PT_WIDTH = width
        cls._PT_PREFIX = prefix
        if cls._PT_PREFIX is None:
            cls._PT_PREFIX = cls._pt_name()
        cls._PT_LKP_INST = {}
        cls._PT_LKP_VALUE = {}
        # Assign values
        assignments = {}
        # Indexed
        if cls._PT_MODE is EnumMode.INDEXED:
            next_val = 0
            for fname, _, fval in cls._pt_definitions():
                if fval is None:
                    fval = next_val
                next_val = fval + 1
                assignments[fname] = fval
        # One-hot
        elif cls._PT_MODE is EnumMode.ONE_HOT:
            next_val = 1
            for fname, _, fval in cls._pt_definitions():
                if fval is None:
                    fval = next_val
                if (math.log2(fval) % 1) != 0:
                    raise EnumError(
                        f"Enum entry {fname} has value {fval} that is not " f"one-hot"
                    )
                next_val = fval << 1
                assignments[fname] = fval
        # Gray code
        elif cls._PT_MODE is EnumMode.GRAY:
            for idx, (fname, _, fval) in enumerate(cls._pt_definitions()):
                gray_val = idx ^ (idx >> 1)
                if fval is None:
                    fval = gray_val
                elif fval != gray_val:
                    raise EnumError(
                        f"Enum entry {fname} has value {fval} that does "
                        f"not conform to the expected Gray code value of {gray_val}"
                    )
                assignments[fname] = fval
        # Determine width
        if cls._PT_WIDTH < 0:
            cls._PT_WIDTH = math.ceil(math.log2(max(assignments.values()) + 1))
        # Final checks
        used = []
        max_val = (1 << cls._PT_WIDTH) - 1
        for fname, fval in assignments.items():
            # Check for oversized values
            if fval > max_val:
                raise EnumError(
                    f"Enum entry {fname} has value {fval} that cannot be "
                    f"encoded in a bit width of {cls._PT_WIDTH}"
                )
            # Check for repeated values
            if fval in used:
                raise EnumError(
                    f"Enum entry {fname} has value {fval} that appears "
                    f"more than once in the enumeration"
                )
            used.append(fval)
            # Create the enum instance
            finst = cls(fval, _pt_bv=BitVector(width=cls._PT_WIDTH))
            setattr(cls, fname, finst)
            cls._PT_LKP_INST[finst] = fname
            cls._PT_LKP_VALUE[fval] = finst

    @property
    def _pt_width(self) -> int:
        return self._PT_WIDTH

    @property
    def _pt_mask(self) -> int:
        return (1 << self._pt_width) - 1

    @property
    def value(self) -> int:
        return int(self._pt_bv)

    @value.setter
    def value(self, value: int) -> int:
        self._pt_set(value)

    def _pt_set(self, value: int) -> None:
        self._pt_bv.set(value)

    def __int__(self) -> int:
        return int(self._pt_bv)

    @classmethod
    def _pt_as_dict(cls) -> dict:
        return {n: int(v) for v, n in cls._PT_LKP_INST.items()}

    @classmethod
    def _pt_cast(cls, value: int) -> None:
        if value in cls._PT_LKP_VALUE:
            return cls._PT_LKP_VALUE[value]
        else:
            return cls(value)
