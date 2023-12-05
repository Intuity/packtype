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

import dataclasses
from typing import Any

from .assembly import Assembly
from .wrap import get_wrapper
from .struct import Struct


class Package(Assembly):

    @classmethod
    def enum(cls, **kwds):
        def _inner(ptcls: Any):
            return ptcls
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
            return ptcls
        return _inner
