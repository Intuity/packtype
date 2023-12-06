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

from .array import Array


class MetaBase(type):
    def __mul__(cls, other: int):
        return Array(cls, other)

    def __rmul__(cls, other: int):
        return cls.__mul__(other)


class Base(metaclass=MetaBase):
    _PT_ALLOW_DEFAULT: bool = False
    _PT_ATTACH = None
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {}
    _PT_DEF = None
    _PT_MEMBERS: list["Base"] = []

    def __init__(self) -> None:
        for attach in (self._PT_ATTACH or []):
            setattr(self, attach.__name__, attach)

    @property
    def _pt_definitions(self) -> list[str, Any]:
        yield from ((x.name, x.type, x.default) for x in dataclasses.fields(self._PT_DEF))
