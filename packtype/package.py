# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import inspect
from collections.abc import Iterable
from typing import Any

from .alias import Alias
from .array import ArraySpec
from .base import Base
from .constant import Constant
from .enum import Enum
from .primitive import NumericPrimitive
from .scalar import Scalar
from .struct import Struct
from .union import Union
from .wrap import get_wrapper
from ordered_set import OrderedSet as OSet


class Package(Base):
    _PT_ALLOW_DEFAULTS: list[type[Base]] = [Constant]
    _PT_FIELDS: dict

    @classmethod
    def _pt_construct(cls, parent: Base) -> None:
        super()._pt_construct(parent)
        cls._PT_FIELDS = {}
        for fname, ftype, fval in cls._pt_definitions():
            if issubclass(ftype, Constant):
                finst = ftype(default=fval)
                setattr(cls, fname, finst)
                finst._PT_ATTACHED_TO = cls
                cls._PT_FIELDS[finst] = fname
            else:
                setattr(cls, fname, ftype)
                ftype._PT_ATTACHED_TO = cls
                cls._PT_FIELDS[ftype] = fname

    @classmethod
    def enum(cls, **kwds):
        def _inner(ptcls: Any):
            enum = get_wrapper(Enum, frame_depth=2)(**kwds)(ptcls)
            cls._PT_ATTACH.append(enum)
            enum._PT_ATTACHED_TO = cls
            setattr(cls, enum.__name__, enum)
            cls._PT_FIELDS[enum] = enum.__name__
            return enum

        return _inner

    @classmethod
    def struct(cls, **kwds):
        def _inner(ptcls: Any):
            struct = get_wrapper(Struct, frame_depth=2)(**kwds)(ptcls)
            cls._PT_ATTACH.append(struct)
            struct._PT_ATTACHED_TO = cls
            setattr(cls, struct.__name__, struct)
            cls._PT_FIELDS[struct] = struct.__name__
            return struct

        return _inner

    @classmethod
    def union(cls, **kwds):
        def _inner(ptcls: Any):
            union = get_wrapper(Union, frame_depth=2)(**kwds)(ptcls)
            cls._PT_ATTACH.append(union)
            union._PT_ATTACHED_TO = cls
            setattr(cls, union.__name__, union)
            cls._PT_FIELDS[union] = union.__name__
            return union

        return _inner

    @classmethod
    def _pt_foreign(cls):
        # Get all referenced types
        all_refs = cls._pt_references()
        # Exclude directly attached types
        foreign = all_refs.difference(OSet(cls._PT_ATTACH).union(cls._pt_field_types()))

        # Exclude non-typedef primitives
        def _is_a_type(obj: Any) -> bool:
            # If this is an ArraySpec, refer to the encapsulated type
            if isinstance(obj, ArraySpec):
                obj = obj.base
            # If it's not a primitive, immediately accept
            if inspect.isclass(obj) and not issubclass(obj, NumericPrimitive):
                return True
            # If not attached to a different package, accept
            return (
                obj._PT_ATTACHED_TO is not None and type(obj._PT_ATTACHED_TO) is not cls
            )

        return OSet(filter(_is_a_type, foreign))

    @property
    def _pt_fields(self) -> dict:
        return self._PT_FIELDS

    @property
    def _pt_constants(self) -> Iterable[Constant]:
        return ((y, x) for x, y in self._pt_fields.items() if isinstance(x, Constant))

    @property
    def _pt_scalars(self) -> Iterable[Scalar]:
        return (
            (y, x)
            for x, y in self._pt_fields.items()
            if (inspect.isclass(x) and issubclass(x, Scalar))
        )

    @property
    def _pt_aliases(self) -> Iterable[Alias]:
        return (
            (y, x)
            for x, y in self._pt_fields.items()
            if inspect.isclass(x) and issubclass(x, Alias)
        )

    @property
    def _pt_enums(self) -> Iterable[Enum]:
        return ((x._pt_name(), x) for x in self._PT_ATTACH if issubclass(x, Enum))

    @property
    def _pt_structs(self) -> Iterable[Struct]:
        return ((x._pt_name(), x) for x in self._PT_ATTACH if issubclass(x, Struct))

    @property
    def _pt_unions(self) -> Iterable[Union]:
        return ((x._pt_name(), x) for x in self._PT_ATTACH if issubclass(x, Union))

    @property
    def _pt_structs_and_unions(self) -> Iterable[Union]:
        return (
            (x._pt_name(), x) for x in self._PT_ATTACH if issubclass(x, Struct | Union)
        )

    @classmethod
    def _pt_lookup(cls, field: type[Base] | Base) -> str:
        return cls._PT_FIELDS[field]
