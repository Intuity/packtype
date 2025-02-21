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

from .array import ArraySpec
from .assembly import Assembly
from .base import Base
from .bitvector import BitVector, BitVectorWindow
from .primitive import NumericPrimitive


class UnionError(Exception):
    pass


class Union(Assembly):
    _PT_WIDTH: int

    def __init__(
        self,
        value: int | None = None,
        default: int | None = None,
        _pt_bv: BitVector | BitVectorWindow | None = None,
    ) -> None:
        super().__init__(_pt_bv=_pt_bv, default=default if value is None else value)
        if value is None:
            value = 0 if default is None else default
        # NOTE: Fields are not constructed at this point, instead they are filled
        #       in lazily as they are requested by the consumer

    def __getattribute__(self, fname: str):
        # Attempt to resolve the attribute from existing properties
        try:
            return super().__getattribute__(fname)
        # If that fails...
        except AttributeError as e:
            # Is this a known field that hasn't yet been instanced?
            if fpair := type(self)._PT_DEF.get(fname, None):
                ftype, fval = fpair
                # Generate an instance of the field
                if isinstance(ftype, ArraySpec):
                    if isinstance(ftype.base, NumericPrimitive):
                        finst = ftype.as_packed(default=fval, _pt_bv=self._pt_bv)
                    else:
                        finst = ftype.as_packed(_pt_bv=self._pt_bv)
                elif issubclass(ftype, NumericPrimitive):
                    finst = ftype(default=fval, _pt_bv=self._pt_bv)
                else:
                    finst = ftype(_pt_bv=self._pt_bv)
                # Attach the instance to the parent
                finst._PT_PARENT = self
                self._pt_force_set(fname, finst)
                # Return it
                return finst
            # If not resolved, forward the attribute error
            else:
                raise e

    @classmethod
    def _pt_construct(cls, parent: Base | None):
        super()._pt_construct(parent)
        cls._PT_WIDTH = None
        for fname, ftype, _ in cls._pt_definitions():
            fwidth = ftype()._pt_width
            if cls._PT_WIDTH is None:
                cls._PT_WIDTH = fwidth
            elif fwidth != cls._PT_WIDTH:
                raise UnionError(
                    f"Union member {fname} has a width of {fwidth} that "
                    f"differs from the expected width of {cls._PT_WIDTH}"
                )

    @property
    def _pt_width(self) -> int:
        return self._PT_WIDTH

    @property
    @functools.cache
    def _pt_mask(self) -> int:
        return (1 << self._pt_width) - 1

    def __int__(self) -> int:
        return self._pt_pack()

    def _pt_pack(self) -> int:
        return int(self._pt_bv)

    @classmethod
    def _pt_unpack(cls, packed: int) -> "Union":
        inst = cls()
        inst._pt_set(packed)
        return inst

    def _pt_set(self, value: int) -> None:
        self._pt_bv.set(value)
