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

from collections.abc import Iterable
from typing import Any


class ArraySpec:
    def __init__(self, base: Any, dimension: int) -> None:
        self.base = base
        self.dimension = dimension

    def _pt_references(self) -> Iterable[Any]:
        return self.base._pt_references()

    @property
    def _PT_ATTACHED_TO(self) -> Any:
        return self.base._PT_ATTACHED_TO

    @_PT_ATTACHED_TO.setter
    def _PT_ATTACHED_TO(self, value: Any) -> None:
        self.base._PT_ATTACHED_TO = value


class Array:
    def __init__(self, spec: ArraySpec, *args, **kwds):
        self._pt_entries = [spec.base(*args, **kwds) for _ in range(spec.dimension)]

    def __getitem__(self, key: int) -> Any:
        return self._pt_entries[key]

    def __setitem__(self, key: int, value: Any) -> Any:
        self._pt_entries[key]._pt_set(value)

    def __iter__(self) -> Iterable[Any]:
        yield from self._pt_entries
