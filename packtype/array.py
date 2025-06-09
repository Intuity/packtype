# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import functools
from collections.abc import Callable, Iterable
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

    def as_packed(self, **kwds) -> "PackedArray":
        return PackedArray(self, **kwds)

    def as_unpacked(self, **kwds) -> "PackedArray":
        return UnpackedArray(self, **kwds)

    def __call__(self, **kwds) -> "PackedArray":
        return self.as_packed(**kwds)


class PackedArray:
    def __init__(
        self,
        spec: ArraySpec,
        *args,
        _pt_bv: BitVector | BitVectorWindow | None = None,
        _pt_per_inst: Callable[
            [int, list[Any], dict[str, Any]], tuple[list[Any], dict[str, Any]]
        ]
        | None = None,
        packing: Packing = Packing.FROM_LSB,
        **kwds,
    ):
        self._pt_bv = BitVector(width=spec._pt_width) if _pt_bv is None else _pt_bv
        self._pt_entries = []
        if packing is Packing.FROM_LSB:
            lsb = 0
            for idx in range(spec.dimension):
                inst_args, inst_kwds = (
                    _pt_per_inst(idx, *args, **kwds)
                    if callable(_pt_per_inst)
                    else (args, kwds)
                )
                self._pt_entries.append(
                    entry := spec.base(
                        *inst_args,
                        _pt_bv=self._pt_bv.create_window(
                            lsb + spec.base._PT_WIDTH - 1, lsb
                        ),
                        **inst_kwds,
                    )
                )
                lsb += entry._pt_width
        else:
            msb = spec._pt_width - 1
            for idx in range(spec.dimension):
                inst_args, inst_kwds = (
                    _pt_per_inst(idx, *args, **kwds)
                    if callable(_pt_per_inst)
                    else (args, kwds)
                )
                self._pt_entries.append(
                    entry := spec.base(
                        *inst_args,
                        _pt_bv=self._pt_bv.create_window(
                            msb, msb - spec.base._PT_WIDTH + 1
                        ),
                        **inst_kwds,
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


class UnpackedArray:
    def __init__(
        self,
        spec: ArraySpec,
        *args,
        _pt_per_inst: Callable[
            [int, list[Any], dict[str, Any]], tuple[list[Any], dict[str, Any]]
        ]
        | None = None,
        **kwds,
    ):
        self._pt_entries = []
        for idx in range(spec.dimension):
            inst_args, inst_kwds = (
                _pt_per_inst(idx, *args, **kwds)
                if callable(_pt_per_inst)
                else (args, kwds)
            )
            self._pt_entries.append(spec.base(*inst_args, **inst_kwds))

    def __getitem__(self, key: int) -> Any:
        return self._pt_entries[key]

    def __setitem__(self, key: int, value: Any) -> Any:
        self._pt_entries[key]._pt_set(value)

    def __iter__(self) -> Iterable[Any]:
        yield from self._pt_entries

    def __len__(self) -> int:
        return len(self._pt_entries)
