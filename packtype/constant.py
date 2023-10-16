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

import math

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
        assert value is None or isinstance(value, int), \
            f"Value must be None or an integer: {value}"
        assert width is None or isinstance(width, (int, Constant)) and width > 0, \
            f"Width must be a positive integer: {width}"
        assert isinstance(signed, bool), \
            f"Signedness must be either True or False: {signed}"
        assert name is None or isinstance(name, str), \
            f"Name must be None or a string: {name}"
        assert desc is None or isinstance(desc, str), \
            f"Description must be None or a string: {name}"
        self.__width  = Constant.clog2(value) if width is None else width
        self.__signed = signed
        self.__name   = name
        self.__desc   = desc
        # Assign the value (performs extra sanity checks)
        if value is not None: self.assign(value)
        else: self.value = None

    def __int__(self):
        return self.value

    def __repr__(self):
        return f"<{type(self).__name__}::{self.__name} value=\"{self.value}\">"

    @staticmethod
    def clog2(value : float) -> int:
        return int(math.ceil(math.log2(value)))

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

    def __hash__(self):
        return hash(self.value)

    def __add__(self, other):
        return int(self.value) + other

    def __sub__(self, other):
        return int(self.value) - other

    def __mul__(self, other):
        return int(self.value) * other

    def __div__(self, other):
        return int(self.value) / other

    def __lshift__(self, other):
        return int(self.value) << other

    def __rshift__(self, other):
        return int(self.value) >> other

    def __eq__(self, other):
        return int(self.value) == other

    def __ne__(self, other):
        return int(self.value) != other

    def __lt__(self, other):
        return int(self.value) < other

    def __le__(self, other):
        return int(self.value) <= other

    def __gt__(self, other):
        return int(self.value) > other

    def __ge__(self, other):
        return int(self.value) >= other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return other - int(self.value)

    def __rmul__(self, other):
        return int(self.value) * other

    def __rdiv__(self, other):
        return other / int(self.value)

    def __rlshift__(self, other):
        return other << int(self.value)

    def __rrshift__(self, other):
        return other >> int(self.value)
