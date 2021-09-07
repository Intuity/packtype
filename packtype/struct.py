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

from .container import Container
from .enum import Enum
from .offset import Offset
from .scalar import Scalar

class Struct(Container):
    """ Packed data structure formed of scalars, enumerations, and other types """

    FROM_LSB = "FROM_LSB"
    FROM_MSB = "FROM_MSB"

    def __init__(self, name, fields, desc=None, width=None, pack=FROM_LSB):
        """ Initialise structure with name and fields

        Args:
            name  : Name of the container
            fields: Dictionary of fields
            desc  : Optional description
            width : Bit width (if omitted is calculated from sum of fields)
        """
        # Perform container construction
        from .union import Union
        super().__init__(name, fields, desc=desc, width=width, legal=[
            Enum, Struct, Union, Scalar
        ])
        # Sanity check width
        assert (width == None) or (isinstance(width, int) or width >= 0), \
            f"Width must be None or a positive integer, not '{width}'"
        # Check the packing mode
        assert pack in (Struct.FROM_LSB, Struct.FROM_MSB), \
            f"Unknown packing mode '{pack}' for {name}"
        assert (pack == Struct.FROM_LSB) or (width != None), \
            "When packing downwards from the MSB, the width must be specified"
        self._pt_pack = pack
        # Determine the position of each field
        if pack == Struct.FROM_MSB:
            next_msb = width - 1
            for field in sorted(self._pt_values(), key=lambda x: x._pt_id):
                base_lsb = next_msb - field._pt_width + 1
                if field._pt_lsb == None:
                    field._pt_lsb = base_lsb
                elif isinstance(field._pt_lsb, Offset):
                    field._pt_lsb = base_lsb - field._pt_lsb.value
                else:
                    assert field._pt_lsb <= base_lsb, \
                        f"Field '{field._pt_name}' of {self._pt_name} specifies " \
                        f"an out-of-order LSB ({field._pt_lsb}), was expecting a " \
                        f"value less than or equal to {base_lsb}"
                next_msb = (field._pt_lsb - 1)
        else:
            next_lsb = 0
            for field in sorted(self._pt_values(), key=lambda x: x._pt_id):
                if field._pt_lsb == None:
                    field._pt_lsb = next_lsb
                elif isinstance(field._pt_lsb, Offset):
                    field._pt_lsb = next_lsb + field._pt_lsb.value
                else:
                    assert field._pt_lsb >= next_lsb, \
                        f"Field '{field._pt_name}' of {self._pt_name} specifies " \
                        f"an out-of-order LSB ({field._pt_lsb}), was expecting a " \
                        f"value greater than or equal to {next_lsb}"
                next_lsb = (field._pt_lsb + field._pt_width)
        # Calculate the width of the struct
        if not self._pt_width and len(self._pt_keys()) > 0:
            self._pt_width = max((
                (x._pt_width + x._pt_lsb) for x in self._pt_values()
            ))
