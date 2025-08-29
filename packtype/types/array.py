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
        self.dimensions = dimensions if isinstance(dimensions, list | tuple) else (dimensions,)

    @property
    def _pt_flat_dimension(self) -> int:
        return math.prod(self.dimensions)

    @property
    def _pt_width(self) -> int:
        return self.base._PT_WIDTH * self._pt_flat_dimension

    @property
    def _PT_WIDTH(self) -> int:  # noqa: N802
        return self._pt_width

    def _pt_ranges(
        self,
        packing: Packing = Packing.FROM_LSB,
    ) -> dict[tuple[int], tuple[int, int]]:
        def _recurse(
            remaining: tuple[int],
            path: tuple[int],
            msb: int,
            lsb: int,
        ) -> tuple[tuple[int], int, int]:
            # If no dimensions left, produce an element
            if len(remaining) == 0:
                yield path, msb, lsb
            # Otherwise, iterate over the dimension
            else:
                dimension, *remaining = remaining
                stepping = math.prod((*remaining, 1)) * self.base._PT_WIDTH
                for idx in range(dimension):
                    if packing is Packing.FROM_LSB:
                        lsb = lsb
                        msb = lsb + stepping - 1
                    else:
                        msb = msb
                        lsb = msb - stepping + 1
                    yield from _recurse(remaining, (*path, idx), msb, lsb)
                    if packing is Packing.FROM_LSB:
                        lsb += stepping
                    else:
                        msb -= stepping

        return {x[0]: (x[1], x[2]) for x in _recurse(self.dimensions, [], self._pt_width - 1, 0)}

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
        dimensions: tuple[int] | None = None,
        dim_path: tuple[int] | None = None,
        **kwds,
    ):
        self._pt_spec = spec
        self._pt_bv = BitVector(width=spec._pt_width) if _pt_bv is None else _pt_bv
        self._pt_entries = []
        self._pt_dimensions = dimensions or spec.dimensions
        self._pt_dim_path = dim_path or []

        # For a single dimension, instance elements
        if len(self._pt_dimensions) == 1:
            msb = self._pt_dimensions[0] * spec.base._PT_WIDTH - 1
            lsb = 0
            for idx in range(self._pt_dimensions[0]):
                if packing is Packing.FROM_LSB:
                    msb = lsb + spec.base._PT_WIDTH - 1
                else:
                    lsb = msb - spec.base._PT_WIDTH + 1
                if callable(_pt_per_inst):
                    inst_args, inst_kwds = _pt_per_inst((*self._pt_dim_path, idx), *args, **kwds)
                else:
                    inst_args, inst_kwds = args, kwds
                self._pt_entries.append(
                    spec.base(
                        *inst_args,
                        _pt_bv=self._pt_bv.create_window(msb, lsb),
                        **inst_kwds,
                    )
                )
                if packing is Packing.FROM_LSB:
                    lsb += spec.base._PT_WIDTH
                else:
                    msb -= spec.base._PT_WIDTH
        # Otherwise, nest another PackedArray
        else:
            dimension, *remaining = self._pt_dimensions
            stepping = math.prod(remaining) * spec.base._PT_WIDTH
            msb = dimension * stepping - 1
            lsb = 0
            for idx in range(dimension):
                if packing is Packing.FROM_LSB:
                    msb = lsb + stepping - 1
                else:
                    lsb = msb - stepping + 1
                if callable(_pt_per_inst):
                    inst_args, inst_kwds = _pt_per_inst((*self._pt_dim_path, idx), *args, **kwds)
                else:
                    inst_args, inst_kwds = args, kwds
                self._pt_entries.append(
                    PackedArray(
                        spec,
                        *args,
                        _pt_bv=self._pt_bv.create_window(msb, lsb),
                        _pt_per_inst=_pt_per_inst,
                        packing=packing,
                        dimensions=remaining,
                        dim_path=(*self._pt_dim_path, idx),
                        **kwds,
                    )
                )
                if packing is Packing.FROM_LSB:
                    lsb += stepping
                else:
                    msb -= stepping

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
        return self._pt_bv.width

    def _pt_pack(self) -> int:
        return int(self._pt_bv)

    @classmethod
    def _pt_unpack(cls, packed: int) -> "PackedArray":
        inst = cls()
        inst._pt_set(packed)
        return inst

    def __int__(self) -> int:
        return self._pt_pack()

    def _pt_set(self, value: int) -> None:
        self._pt_bv.set(value)


class UnpackedArray:
    def __init__(
        self,
        spec: ArraySpec,
        *args,
        _pt_per_inst: Callable[[int, list[Any], dict[str, Any]], tuple[list[Any], dict[str, Any]]]
        | None = None,
        **kwds,
    ):
        self._pt_spec = spec
        self._pt_entries = []
        for idx in range(spec.dimensions[0]):
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
