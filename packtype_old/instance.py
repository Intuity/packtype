# Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk
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

from typing import Iterable

from .base import Base
from .container import Container
from .constant import Constant
from .offset import Offset

class Instance(Base):
    """ Instance of a container """

    def __init__(self, container, name=None, lsb=None, desc=None):
        """ Initialise the instance

        Args:
            container: The container type (e.g. an Enum, Constant, etc)
            name     : Optional name of the instance
            lsb      : Least significant bit when positioned in a larger structure
            desc     : Optional description of the instance
        """
        super().__init__()
        assert isinstance(container, Container), \
            f"Container must be an instance of the Container type: {type(container)}"
        assert name is None or isinstance(name, str), \
            f"Name must be None or a string: {name}"
        assert lsb is None or (isinstance(lsb, int) and lsb >= 0) or isinstance(lsb, Offset), \
            f"LSB must be None or a positive integer: {lsb}"
        assert desc is None or isinstance(desc, str), \
            f"Description must be None or a string: {desc}"
        self.__container = container
        self.__name      = name
        self.__lsb       = lsb
        self.__desc      = desc

    @property
    def _pt_container(self):
        return self.__container

    @property
    def _pt_width(self):
        return self.__container._pt_width

    @property
    def _pt_name(self):
        return self.__name
    @_pt_name.setter
    def _pt_name(self, name):
        assert not self.__name, f"Trying to change name of instance {self.__name}"
        assert isinstance(name, str), f"Name must be a string: {name}"
        self.__name = name

    @property
    def _pt_lsb(self):
        return self.__lsb
    @_pt_lsb.setter
    def _pt_lsb(self, lsb):
        assert not self.__lsb or isinstance(self.__lsb, Offset), \
            f"Trying to change LSB of instance {self.__lsb}"
        assert isinstance(lsb, int) and lsb >= 0, \
            f"LSB must be a positive integer: {lsb}"
        self.__lsb = lsb

    @property
    def _pt_msb(self):
        return (self.__lsb + self._pt_width - 1)

    @property
    def _pt_mask(self):
        return ((1 << self._pt_width) - 1)

    @property
    def _pt_desc(self):
        return self.__desc

    @property
    def _pt_parent(self):
        return self.__container._pt_parent

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self.__container, name)

    def __mul__(self, other):
        return Array(self.__container, other, self.__name, self.__lsb, self.__desc)

    def __rmul__(self, other):
        return self.__mul__(other)

    def _pt_foreign(self, exclude: list["Container"] | None = None) -> Iterable["Container"]:
        """
        Identify all foreign types referenced by this container and any of its
        children, excluding types that inherit from a provided list of parents.

        :param exclude: Parent objects to exclude
        :returns: The set of foreign types
        """
        yield from self.__container._pt_foreign(exclude)

class Array(Instance):
    """
    Arrayed instance of a container

    :param container: The container type (e.g. an Enum, Constant, etc)
    :param count:     Number of instances
    :param name:      Optional name of the instance
    :param desc:      Optional description of the instance
    """

    def __init__(self, container, count, name=None, lsb=None, desc=None):
        super().__init__(container, name, lsb, desc)
        self.count = count
        assert isinstance(count, (int, Constant)) and count >= 0, \
            f"Array count must be a positive integer"
        self.__count = count

    @property
    def _pt_count(self):
        return self.__count

    @property
    def _pt_width(self):
        return int(self.__count) * int(super()._pt_width)
