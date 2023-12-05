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

import functools

from .base import Base


class ValueError(Exception):
    pass


class MetaPrimitive(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

    def __getitem__(cls, width):
        assert isinstance(width, int), "Width must be an integer"
        return MetaPrimitive.get_variant(cls, width)

    @functools.cache
    def get_variant(prim: "Primitive", width: int):
        return type(prim.__name__ + f"_{width}",
                    (prim, ),
                    {"_PT_WIDTH": width})


class Primitive(Base, metaclass=MetaPrimitive):
    _PT_WIDTH : int = -1

    def __init__(self, default: int | None = None) -> None:
        if type(self)._PT_ALLOW_DEFAULT:
            self.__value = default
        else:
            self.__value = 0

    @property
    def _pt_width(self) -> int:
        return type(self)._PT_WIDTH

    @property
    def _pt_mask(self) -> int:
        return ((1 << type(self)._PT_WIDTH) - 1)

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, value: int) -> int:
        self._pt_set(value)

    def _pt_set(self, value: int) -> int:
        if value < 0 or value > self._pt_mask:
            raise ValueError(
                f"Value {value} cannot be represented by {self._pt_width} bits"
            )
        self.__value = value

    def __int__(self) -> int:
        return self.__value
