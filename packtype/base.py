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
from typing import Any, Optional

from .array import ArraySpec


class MetaBase(type):
    def __mul__(cls, other: int):
        return ArraySpec(cls, other)

    def __rmul__(cls, other: int):
        return ArraySpec(cls, other)


class Base(metaclass=MetaBase):
    # Whether a default value can be assigned (e.g. constant value)
    _PT_ALLOW_DEFAULT: bool = False
    # Any other types to be attached to this one (e.g. struct to a package)
    _PT_ATTACH: list[type["Base"]] | None = None
    # Points upwards from an attached type to what it's attached to
    _PT_ATTACHED_TO: type["Base"] | None = None
    # Attributes specific to a type (e.g. width of a struct)
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {}
    # The dataclass definition
    _PT_DEF = None
    # A shared instance will be created as the imposter rather than a class, this
    # is used for defining packages
    _PT_SHARED: bool = False
    # Tuple of source file and line number where the type is defined
    _PT_SOURCE: tuple[str, int] = ("?", 0)

    def __init__(self, parent: Optional["Base"] = None) -> None:
        self._pt_parent = parent

    @classmethod
    def _pt_name(cls):
        return cls.__name__

    @property
    def _pt_definitions(self) -> list[str, Any]:
        yield from (
            (x.name, x.type, x.default) for x in dataclasses.fields(self._PT_DEF)
        )

    def _pt_updated(self, *path: "Base"):
        if self._pt_parent is not None:
            self._pt_parent._pt_updated(self, *path)

    @classmethod
    def _pt_field_types(cls) -> list[type["Base"]]:
        if cls._PT_DEF:
            return {x.type for x in dataclasses.fields(cls._PT_DEF)}
        else:
            return set()

    @classmethod
    def _pt_references(cls) -> list[type["Base"]]:
        # If no definition, return early
        if not cls._PT_DEF:
            return set()
        # Else iterate through core fields
        collect = set()
        for ftype in cls._pt_field_types():
            collect.update(ftype._pt_references())
            collect.add(ftype)
        # ...and through attached fields
        for field in cls._PT_ATTACH or []:
            collect.update(field._pt_references())
            collect.add(field)
        return collect
