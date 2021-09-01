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
from .constant import Constant
from .offset import Offset

class Scalar(Base):
    """ Scalar type with a fixed size """

    def __init__(self, width=32, signed=False, lsb=None, name=None, desc=None):
        """ Initialise the scalar

        Args:
            width : Bit-width of the scalar (default: 32)
            signed: Whether the scalar holds a signed value
            lsb   : Optional least-significant bit
            name  : Optional name of the scalar
            desc  : Optional description of the scalar
        """
        # Perform base construction
        super().__init__()
        # Convert arguments from constants if required
        if isinstance(width,  Constant): width  = width.value
        if isinstance(signed, Constant): signed = signed.value
        if isinstance(lsb,    Constant): lsb    = lsb.value
        # Check arguments
        assert isinstance(width, int) and width > 0, \
            f"Width must be a positive integer: {width}"
        assert isinstance(signed, bool), \
            f"Signedness must be either True or False: {signed}"
        assert lsb == None or (isinstance(lsb, int) and lsb >= 0) or isinstance(lsb, Offset), \
            f"Least significant bit must be None or an integer: {lsb}"
        assert name == None or isinstance(name, str), \
            f"Name must be None or a string: {name}"
        assert desc == None or isinstance(desc, str), \
            f"Description must be None or a string: {desc}"
        self.__width  = width
        self.__signed = signed
        self.__lsb    = lsb
        self.__name   = name
        self.__desc   = desc

    @property
    def _pt_width(self):
        return self.__width

    @property
    def _pt_signed(self):
        return self.__signed

    @property
    def _pt_lsb(self):
        return self.__lsb
    @_pt_lsb.setter
    def _pt_lsb(self, lsb):
        assert self.__lsb == None or isinstance(self.__lsb, Offset), \
            f"Trying to alter LSB of scalar {self.__name}"
        assert isinstance(lsb, int) and lsb >= 0, \
            f"LSB must be a positive integer: {lsb}"
        self.__lsb = lsb

    @property
    def _pt_msb(self):
        return (self.__lsb + self.__width - 1)

    @property
    def _pt_mask(self):
        return ((1 << self.__width) - 1)

    @property
    def _pt_name(self):
        return self.__name
    @_pt_name.setter
    def _pt_name(self, name):
        assert not self.__name, f"Trying to alter name of scalar {self.__name}"
        assert isinstance(name, str), f"Name must be a string: {name}"
        self.__name = name

    @property
    def _pt_desc(self):
        return self.__desc
    @_pt_desc.setter
    def _pt_desc(self, desc):
        assert not self.__desc, f"Trying to alter description of scalar {self.__name}"
        assert isinstance(desc, str), f"Description must be a string: {desc}"
        self.__desc = desc
