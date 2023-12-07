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

from typing import Any, Iterable

from .alias import Alias
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
        self._pt_fields = []
        for fname, ftype, fval in self._pt_definitions:
            if issubclass(ftype, Constant):
                finst = ftype(default=fval)
                setattr(self, fname, finst)
                self._pt_fields.append((fname, finst))
            else:
                setattr(self, fname, ftype)
                self._pt_fields.append((fname, ftype))

    def __call__(self) -> "Package":
        return self

    @classmethod
    def enum(cls, **kwds):
        def _inner(ptcls: Any):
            enum = get_wrapper(Enum, frame_depth=2)(**kwds)(ptcls)
            cls._PT_ATTACH.append(enum)
            enum._PT_ATTACHED_TO = cls
            return enum
        return _inner

    @classmethod
    def struct(cls, **kwds):
        def _inner(ptcls: Any):
            struct = get_wrapper(Struct, frame_depth=2)(**kwds)(ptcls)
            cls._PT_ATTACH.append(struct)
            struct._PT_ATTACHED_TO = cls
            return struct
        return _inner

    @classmethod
    def union(cls, **kwds):
        def _inner(ptcls: Any):
            union = get_wrapper(Union, frame_depth=2)(**kwds)(ptcls)
            cls._PT_ATTACH.append(union)
            union._PT_ATTACHED_TO = cls
            return union
        return _inner

    @classmethod
    def _pt_foreign(cls):
        # Get all referenced types
        all_refs = cls._pt_references()
        # Exclude directly attached types
        foreign = all_refs.difference(set(cls._PT_ATTACH).union(cls._pt_field_types()))
        # Exclude primitives (constants and scalars)
        return {x for x in foreign if not issubclass(x, Primitive)}

    @property
    def _pt_constants(self) -> Iterable[Constant]:
        return ((x, y) for x, y in self._pt_fields if isinstance(y, Constant))

    @property
    def _pt_scalars(self) -> Iterable[Scalar]:
        return ((x, y) for x, y in self._pt_fields if isinstance(y, Scalar))

    @property
    def _pt_aliases(self) -> Iterable[Alias]:
        return ((x, y) for x, y in self._pt_fields if isinstance(y, Alias))

    @property
    def _pt_enums(self) -> Iterable[Enum]:
        return ((x._pt_name, x) for x in self._PT_ATTACH if issubclass(x, Enum))

    @property
    def _pt_structs(self) -> Iterable[Struct]:
        return ((x.__name__, x) for x in self._PT_ATTACH if issubclass(x, Struct))

    @property
    def _pt_unions(self) -> Iterable[Union]:
        return ((x.__name__, x) for x in self._PT_ATTACH if issubclass(x, Union))

    @property
    def _pt_structs_and_unions(self) -> Iterable[Union]:
        return ((x.__name__, x) for x in self._PT_ATTACH if issubclass(x, Struct | Union))
