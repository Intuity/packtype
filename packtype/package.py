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

import inspect
from collections.abc import Iterable
from typing import Any

from .alias import Alias
from .array import ArraySpec
from .base import Base
from .constant import Constant
from .enum import Enum
from .primitive import Primitive
from .scalar import Scalar
from .struct import Struct
from .union import Union
from .wrap import get_wrapper


class Package(Base):
    _PT_SHARED: bool = True

    def __init__(self, parent: Base | None = None) -> None:
        super().__init__(parent)
        self._pt_fields = {}
        for fname, ftype, fval in self._pt_definitions():
            if issubclass(ftype, Constant):
                finst = ftype(default=fval)
                setattr(self, fname, finst)
                finst._PT_ATTACHED_TO = self
                self._pt_fields[finst] = fname
            else:
                setattr(self, fname, ftype)
                ftype._PT_ATTACHED_TO = self
                self._pt_fields[ftype] = fname

    def __call__(self) -> "Package":
        return self

    def enum(self, **kwds):
        def _inner(ptcls: Any):
            enum = get_wrapper(Enum, frame_depth=2)(**kwds)(ptcls)
            type(self)._PT_ATTACH.append(enum)
            enum._PT_ATTACHED_TO = self
            setattr(self, enum.__name__, enum)
            self._pt_fields[enum] = enum.__name__
            return enum

        return _inner

    def struct(self, **kwds):
        def _inner(ptcls: Any):
            struct = get_wrapper(Struct, frame_depth=2)(**kwds)(ptcls)
            type(self)._PT_ATTACH.append(struct)
            struct._PT_ATTACHED_TO = self
            setattr(self, struct.__name__, struct)
            self._pt_fields[struct] = struct.__name__
            return struct

        return _inner

    def union(self, **kwds):
        def _inner(ptcls: Any):
            union = get_wrapper(Union, frame_depth=2)(**kwds)(ptcls)
            type(self)._PT_ATTACH.append(union)
            union._PT_ATTACHED_TO = self
            setattr(self, union.__name__, union)
            self._pt_fields[union] = union.__name__
            return union

        return _inner

    @classmethod
    def _pt_foreign(cls):
        # Get all referenced types
        all_refs = cls._pt_references()
        # Exclude directly attached types
        foreign = all_refs.difference(set(cls._PT_ATTACH).union(cls._pt_field_types()))

        # Exclude non-typedef primitives
        def _is_a_type(obj: Any) -> bool:
            # If this is an ArraySpec, refer to the encapsulated type
            if isinstance(obj, ArraySpec):
                obj = obj.base
            # If it's not a primitive, immediately accept
            if inspect.isclass(obj) and not issubclass(obj, Primitive):
                return True
            # If not attached to a different package, accept
            return (
                obj._PT_ATTACHED_TO is not None and type(obj._PT_ATTACHED_TO) is not cls
            )

        return set(filter(_is_a_type, foreign))

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

    def _pt_lookup(self, field: type[Base] | Base) -> str:
        return self._pt_fields[field]
