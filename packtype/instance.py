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

from .base import Base
from .container import Container
from .offset import Offset

class Instance(Base):
    """ Instance of a container """

    def __init__(self, container, name=None, lsb=None, desc=None):
        """ Initialise the instance

        Args:
            container: The container type (e.g. an Enum, Constant, etc)
            name     : Optional name of the instance
            desc     : Optional description of the instance
        """
        super().__init__()
        assert isinstance(container, Container), \
            f"Container must be an instance of the Container type: {type(container)}"
        assert name == None or isinstance(name, str), \
            f"Name must be None or a string: {name}"
        assert lsb == None or (isinstance(lsb, int) and lsb >= 0) or isinstance(lsb, Offset), \
            f"LSB must be None or a positive integer: {lsb}"
        assert desc == None or isinstance(desc, str), \
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

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self.__container, name)
