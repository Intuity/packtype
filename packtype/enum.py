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

from .constant import Constant
from .container import Container

class Enum(Container):
    """ Enumerated value made up of constants """

    INDEXED = "INDEXED" # Assigns values 0, 1, 2, 3, ...
    ONEHOT  = "ONEHOT"  # Assigns values 1, 2, 4, 8, ...
    GRAY    = "GRAY"    # Assigns variable sized Gray code

    def __init__(self, name, fields, desc=None, width=None, mode=INDEXED):
        """ Initialise enumeration with a name and fields

        Args:
            name  : Name of the container
            fields: Dictionary of fields
            width : Bit width (if omitted is calculated from largest value)
            mode  : How named values should be enumerated
        """
        # Perform container construction
        super().__init__(name, fields, desc=desc, width=width, legal=[Constant])
        # Check mode is acceptable
        assert mode in (Enum.INDEXED, Enum.ONEHOT, Enum.GRAY), \
            f"Enum {name} mode must be INDEXED, ONEHOT, or GRAY: {mode}"
        self.__mode = mode
        # Check enumeration and assign missing values
        consts    = sorted([_ for _ in self._pt_items()], key=lambda x: x[1]._pt_id)
        allocated = []
        next_val  = {
            Enum.ONEHOT : 1,
            Enum.INDEXED: 0,
            Enum.GRAY   : 0,
        }[self.__mode]
        for idx, (key, const) in enumerate(consts):
            # If value is None, assign the next in the sequence
            if const.value == None: const.value = next_val
            # Set the next value to follow on
            next_val = const.value
            if   self.__mode == Enum.INDEXED: next_val  += 1
            elif self.__mode == Enum.ONEHOT : next_val <<= 1
            elif self.__mode == Enum.GRAY   : next_val   = ((idx + 1) ^ ((idx + 1) >> 1))
            # Check the value is legal
            assert const.value >= 0, \
                f"Enumeration {name} contains negative value {const.value} ({key})"
            if self.__mode == Enum.ONEHOT:
                assert const.value > 0 and ((math.log2(const.value) % 1) == 0), \
                    f"Value {const.value} ({key}) of {name} is not one-hot"
            elif self.__mode == Enum.GRAY:
                gray_val = (idx ^ (idx >> 1))
                assert const.value == gray_val, \
                    f"Value {const.value} ({key}) at index {idx} of {name} is " \
                    f"not gray-coded"
            if self._pt_width != None:
                assert const.value < (1 << self._pt_width), \
                    f"Value {const.value} ({key}) of {name} cannot be encoded " \
                    f"within {self._pt_width} bits"
            # Check the value isn't repeated
            assert const.value not in allocated, \
                f"Value {const.value} ({key}) appears twice in {name}"
            # Track allocated values
            allocated.append(const.value)
        # If no width was provided, calculate it
        if not self._pt_width and len(self._pt_keys()) > 0:
            self._pt_width = int(math.ceil(math.log2(max(allocated)+1)))

    @property
    def _pt_mode(self):
        return self.__mode
