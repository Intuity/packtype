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

    def __init__(self, value=None, width=32, signed=False, name=None, desc=None):
        """ Initialise the value

        Args:
            value : Optional specification of the value
            width : Bit-width of the constant (default: 32)
            signed: Whether the constant takes a signed value
            name  : Optional name of the constant
            desc  : Optional description of the constant
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
        self.width  = width
        self.signed = signed
        self.name   = name
        self.desc   = desc
        # Assign the value (performs extra sanity checks)
        if value != None: self.assign(value)
        else: self.value = None

    def __int__(self):
        return self.value

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