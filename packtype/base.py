# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import functools
from collections import defaultdict
from typing import Any

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self  # noqa: UP035

from .alias import MetaAlias
from .array import ArraySpec
from .bitvector import BitVector
from ordered_set import OrderedSet as OSet


class MetaBase(type):
    def __mul__(cls, other: int):
        return ArraySpec(cls, other)

    def __rmul__(cls, other: int):
        return ArraySpec(cls, other)


class Base(metaclass=MetaBase):
    # The base class type
    _PT_BASE: type["Base"] | None = None
    # What contained types are allowed to have a default value (e.g. constants)
    _PT_ALLOW_DEFAULTS: list[type["Base"]] = []
    # Any other types to be attached to this one (e.g. struct to a package)
    _PT_ATTACH: list[type["Base"]] | None = None
    # Points upwards from an attached type to what it's attached to
    _PT_ATTACHED_TO: type["Base"] | None = None
    # Attributes specific to a type (e.g. width of a struct)
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {}
    # Bit width
    _PT_WIDTH: int = 0
    # The fields definition
    _PT_DEF: dict[str, tuple[type["Base"], Any]] = {}
    # Tuple of source file and line number where the type is defined
    _PT_SOURCE: tuple[str, int] = ("?", 0)
    # Handle to parent
    _PT_PARENT: Self = None
    # Profiling
    _PT_PROFILING: dict[str, int] = defaultdict(lambda: 0)

    def __init__(self, _pt_bv: BitVector | None = None, default: int | None = None) -> None:
        self._pt_bv = _pt_bv
        if self._pt_bv is None:
            self._pt_bv = BitVector(width=self._PT_WIDTH)
            self._pt_bv.set(0 if default is None else default)
        self._PT_PROFILING[type(self).__name__] += 1

    @classmethod
    def _pt_construct(cls, parent: Self | None = None, **_kwds):
        del _kwds
        cls._PT_PARENT = parent

    @classmethod
    def _pt_name(cls):
        return cls.__name__

    @classmethod
    @functools.cache
    def _pt_definitions(cls) -> list[str, Any]:
        return [(n, t, d) for n, (t, d) in cls._PT_DEF.items()]

    @classmethod
    def _pt_field_types(cls) -> list[type["Base"]]:
        if cls._PT_DEF:
            return OSet(t for t, _ in cls._PT_DEF.values())
        else:
            return OSet()

    @classmethod
    def _pt_references(cls) -> list[type["Base"]]:
        def _unwrap(obj):
            # Unwrap arrays
            if isinstance(obj, ArraySpec):
                obj = obj.base
            # Unwrap aliased types
            if issubclass(type(obj), MetaAlias):
                obj = obj._PT_ALIAS
            return obj
        # Else iterate through core fields
        collect = OSet()
        for ftype in map(_unwrap, cls._pt_field_types()):
            collect.update(ftype._pt_references())
            collect.add(ftype)
        # ...and through attached fields
        for field in map(_unwrap, cls._PT_ATTACH or []):
            collect.update(field._pt_references())
            collect.add(field)
        return collect

    @property
    def _pt_parent(self) -> Self:
        return self._PT_PARENT

    @classmethod
    def _pt_enable_profiling(cls, limit: int = 1) -> None:
        """
        Enable tracking of Packtype object creation

        :param limit: Don't print out statistics for objects below this limit
        """
        import atexit

        def _list_objs():
            print("Packtype object creation counts:")
            for obj, cnt in sorted(
                Base._PT_PROFILING.items(), key=lambda x: x[1], reverse=True
            ):
                if cnt > limit:
                    print(f"{cnt:10d}: {obj}")

        atexit.register(_list_objs)
