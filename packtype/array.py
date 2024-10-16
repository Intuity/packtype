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
from collections.abc import Iterable
from typing import Any

from .bitvector import BitVector, BitVectorWindow
from .packing import Packing


class ArraySpec:
    def __init__(self, base: Any, dimension: int) -> None:
        self.base = base
        self.dimension = dimension

    @property
    def _PT_WIDTH(self) -> int:
        return self.base._PT_WIDTH * self.dimension

    @property
    def _pt_width(self) -> int:
        return self._PT_WIDTH

    def _pt_references(self) -> Iterable[Any]:
        return self.base._pt_references()

    def __call__(self, **kwds) -> "Array":
        return Array(self, **kwds)


class Array:
    def __init__(
        self,
        spec: ArraySpec,
        *args,
        _pt_bv: BitVector | BitVectorWindow | None = None,
        packing: Packing = Packing.FROM_LSB,
        **kwds,
    ):
        self._pt_bv = BitVector(width=spec._pt_width) if _pt_bv is None else _pt_bv
        self._pt_entries = []
        if packing is Packing.FROM_LSB:
            lsb = 0
            for _ in range(spec.dimension):
                self._pt_entries.append(
                    entry := spec.base(
                        *args,
                        _pt_bv=self._pt_bv.create_window(
                            lsb + spec.base._PT_WIDTH - 1, lsb
                        ),
                        **kwds,
                    )
                )
                lsb += entry._pt_width
        else:
            msb = spec._pt_width - 1
            for _ in range(spec.dimension):
                self._pt_entries.append(
                    entry := spec.base(
                        *args,
                        _pt_bv=self._pt_bv.create_window(
                            msb, msb - spec.base._PT_WIDTH + 1
                        ),
                        **kwds,
                    )
                )
                msb -= entry._pt_width

    def __getitem__(self, key: int) -> Any:
        return self._pt_entries[key]

    def __setitem__(self, key: int, value: Any) -> Any:
        self._pt_entries[key]._pt_set(value)

    def __iter__(self) -> Iterable[Any]:
        yield from self._pt_entries

    def __len__(self) -> int:
        return len(self._pt_entries)

    @property
    @functools.cache
    def _pt_width(self) -> int:
        return sum(x._pt_width for x in self._pt_entries)
