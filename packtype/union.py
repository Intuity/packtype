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

from .assembly import Assembly
from .base import Base


class UnionError(Exception):
    pass


class Union(Assembly):
    _PT_WIDTH: int

    def __init__(self, value: int = 0) -> None:
        super().__init__()
        self._pt_updating = False
        self._pt_set(value)

    @classmethod
    def _pt_construct(cls, parent: Base | None):
        super()._pt_construct(parent)
        cls._PT_WIDTH = None
        for fname, ftype, _ in cls._pt_definitions():
            fwidth = ftype()._pt_width
            if cls._PT_WIDTH is None:
                cls._PT_WIDTH = fwidth
            elif fwidth != cls._PT_WIDTH:
                raise UnionError(
                    f"Union member {fname} has a width of {fwidth} that "
                    f"differs from the expected width of {cls._PT_WIDTH}"
                )

    @property
    def _pt_width(self) -> int:
        return self._PT_WIDTH

    @property
    def _pt_mask(self) -> int:
        return (1 << self._pt_width) - 1

    def __int__(self) -> int:
        return self._pt_pack()

    def _pt_pack(self) -> int:
        values = list({int(x) for x in self._pt_fields.keys()})
        if len(values) != 1 or values[0] != self._pt_raw:
            raise UnionError(
                f"Multiple member values were discovered when packing a "
                f"{type(self).__name__} union - expected a value of "
                f"0x{self._pt_raw:X} but saw " + ", ".join(f"0x{x:X}" for x in values)
            )
        return self._pt_raw

    @classmethod
    def _pt_unpack(cls, packed: int) -> "Union":
        inst = cls()
        inst._pt_set(packed)
        return inst

    def _pt_set(self, value: int, force: bool = False) -> None:
        # Capture raw value
        self._pt_raw = value & self._pt_mask
        # Broadcast to all members
        for field in self._pt_fields.keys():
            field._pt_set(self._pt_raw, force=True)
        # Flag update
        if not force:
            self._pt_updated(self)

    def _pt_updated(self, obj: Base, *path: Base):
        # Block nested updates to avoid an infinite loop
        if self._pt_updating:
            return
        # Set the lock
        self._pt_updating = True
        # Update the raw value and all members (except the 'obj')
        self._pt_raw = int(obj)
        for field in self._pt_fields.keys():
            if field is not obj:
                field._pt_set(self._pt_raw, force=True)
        # Clear the lock
        self._pt_updating = False
        # Propagate update to the parent
        super()._pt_updated(self, obj, *path)
