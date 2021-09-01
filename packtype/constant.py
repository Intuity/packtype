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

class Constant(Base):
    """ Constant value with a fixed size """

    def __init__(self, desc=None, value=None, width=32, signed=False, name=None):
        """ Initialise the value

        Args:
            desc  : Optional description of the constant
            value : Optional specification of the value
            width : Bit-width of the constant (default: 32)
            signed: Whether the constant takes a signed value
            name  : Optional name of the constant
        """
        super().__init__()
        assert value == None or isinstance(value, int), \
            f"Value must be None or an integer: {value}"
        assert isinstance(width, int) and width > 0, \
            f"Width must be a positive integer: {width}"
        assert isinstance(signed, bool), \
            f"Signedness must be either True or False: {signed}"
        assert name == None or isinstance(name, str), \
            f"Name must be None or a string: {name}"
        assert desc == None or isinstance(desc, str), \
            f"Description must be None or a string: {name}"
        self.__width  = width
        self.__signed = signed
        self.__name   = name
        self.__desc   = desc
        # Assign the value (performs extra sanity checks)
        if value != None: self.assign(value)
        else: self.value = None

    def __int__(self):
        return self.value

    @property
    def width(self):
        return self.__width
    @property
    def _pt_width(self):
        return self.__width

    @property
    def signed(self):
        return self.__signed
    @property
    def _pt_signed(self):
        return self.__signed

    @property
    def name(self):
        return self.__name
    @property
    def _pt_name(self):
        return self.__name
    @_pt_name.setter
    def _pt_name(self, name):
        assert not self.__name, f"Trying to override name of {self.__name}: {name}"
        assert isinstance(name, str), f"Name must be None or a string: {name}"
        self.__name = name

    @property
    def desc(self):
        return self.__desc
    @property
    def _pt_desc(self):
        return self.__desc
    @_pt_desc.setter
    def _pt_desc(self, desc):
        assert not self.__desc, f"Trying to alter description of constant {self.__name}"
        assert isinstance(desc, str), f"Description must be a string: {desc}"
        self.__desc = desc

    def assign(self, value):
        assert isinstance(value, int), f"Value must be an integer: {value}"
        if self.signed:
            assert (
                (value >= (-1 * (1 << (self.width - 1)))) and
                (value <  (1 << (self.width - 1)))
            ), f"Value {value} is outside of a signed {self.width} bit range"
        else:
            assert value >= 0 and value < (1 << self.width), \
                f"Value {value} is outside of an unsigned {self.width} bit range"
        self.value = value
