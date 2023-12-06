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

from typing import Any

from .base import Base
from .constant import Constant
from .enum import Enum
from .wrap import get_wrapper
from .struct import Struct
from .union import Union


class Package(Base):

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

    @classmethod
    def enum(cls, **kwds):
        def _inner(ptcls: Any):
            enum = get_wrapper(Enum)(**kwds)(ptcls)
            cls._PT_ATTACH.append(enum)
            return enum
        return _inner

    @classmethod
    def struct(cls, **kwds):
        def _inner(ptcls: Any):
            struct = get_wrapper(Struct)(**kwds)(ptcls)
            cls._PT_ATTACH.append(struct)
            return struct
        return _inner

    @classmethod
    def union(cls, **kwds):
        def _inner(ptcls: Any):
            union = get_wrapper(Union)(**kwds)(ptcls)
            cls._PT_ATTACH.append(union)
            return union
        return _inner
