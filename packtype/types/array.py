# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import functools
import math
from collections.abc import Callable, Iterable
from typing import Any, Self

from .bitvector import BitVector, BitVectorWindow
from .packing import Packing


class ArraySpec:
    def __init__(self, base: Any, dimensions: int | tuple[int]) -> None:
        self.base = base
        self.dimensions = (dimensions, ) if isinstance(dimensions, int) else dimensions

    @property
    def _pt_flat_dimension(self) -> int:
        return math.prod(self.dimensions)

    @property
    def _pt_width(self) -> int:
        return self.base._PT_WIDTH * self._pt_flat_dimension

    @property
    def _PT_WIDTH(self) -> int:  # noqa: N802
        return self._pt_width

    def _pt_references(self) -> Iterable[Any]:
        return self.base._pt_references()

    def as_packed(self, **kwds) -> "PackedArray":
        return PackedArray(self, **kwds)

    def as_unpacked(self, **kwds) -> "PackedArray":
        return UnpackedArray(self, **kwds)

    def __call__(self, **kwds) -> "PackedArray":
        return self.as_packed(**kwds)

    def __getitem__(self, key: int) -> Self:
        return type(self)(self.base, (key, *self.dimensions))

class PackedArray:
    def __init__(
        self,
        spec: ArraySpec,
        *args,
        _pt_bv: BitVector | BitVectorWindow | None = None,
        _pt_per_inst: Callable[[int, list[Any], dict[str, Any]], tuple[list[Any], dict[str, Any]]]
        | None = None,
        packing: Packing = Packing.FROM_LSB,
        **kwds,
    ):
        self._pt_bv = BitVector(width=spec._pt_width) if _pt_bv is None else _pt_bv
        self._pt_entries = []

        def _recurse_dimension(
            remaining: tuple[int],
            path: tuple[int],
            msb: int,
            lsb: int,
        ):
            # If no dimensions left, produce an element
            if len(remaining) == 0:
                if callable(_pt_per_inst):
                    inst_args, inst_kwds = _pt_per_inst(path, *args, **kwds)
                else:
                    inst_args, inst_kwds = args, kwds
                print(f"Creating window {msb}:{lsb} for {path}")
                return spec.base(
                    *inst_args,
                    _pt_bv=self._pt_bv.create_window(msb, lsb),
                    **inst_kwds,
                )
            # Otherwise, iterate over the dimension
            else:
                dimension, *remaining = remaining
                stepping = math.prod((*remaining, 1)) * spec.base._PT_WIDTH
                entries = []
                for idx in range(dimension):
                    if packing is Packing.FROM_LSB:
                        lsb = lsb
                        msb = lsb + stepping - 1
                    else:
                        msb = msb
                        lsb = msb - stepping + 1
                    entries.append(_recurse_dimension(
                        remaining,
                        (*path, idx),
                        msb,
                        lsb,
                    ))
                    if packing is Packing.FROM_LSB:
                        lsb += stepping
                    else:
                        msb -= stepping
                return entries

        self._pt_entries = _recurse_dimension(
            spec.dimensions,
            [],
            spec._pt_width - 1,
            0,
        )

    def __getitem__(self, key: int) -> Any:
        return self._pt_entries[key]

    def __setitem__(self, key: int, value: Any) -> Any:
        self._pt_entries[key]._pt_set(value)

    def __iter__(self) -> Iterable[Any]:
        yield from self._pt_entries

    def __len__(self) -> int:
        return len(self._pt_entries)

    @property
    @functools.cache  # noqa: B019
    def _pt_width(self) -> int:
        return sum(x._pt_width for x in self._pt_entries)


class UnpackedArray:
    def __init__(
        self,
        spec: ArraySpec,
        *args,
        _pt_per_inst: Callable[[int, list[Any], dict[str, Any]], tuple[list[Any], dict[str, Any]]]
        | None = None,
        **kwds,
    ):
        self._pt_entries = []
        for idx in range(spec.dimension):
            inst_args, inst_kwds = (
                _pt_per_inst(idx, *args, **kwds) if callable(_pt_per_inst) else (args, kwds)
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
