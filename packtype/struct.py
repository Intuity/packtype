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
from .offset import Offset

class Struct(Container):
    """ Packed data structure formed of scalars, enumerations, and other types """

    def __init__(self, name, fields, width=None):
        """ Initialise structure with name and fields

        Args:
            name  : Name of the container
            fields: Dictionary of fields
            width : Bit width (if omitted is calculated from sum of fields)
        """
        # Perform container construction
        super().__init__(name, fields, width=width)
        # Setup the LSB for each field
        next_lsb = 0
        for field in sorted(self._pt_values(), key=lambda x: x._pt_id):
            if field._pt_lsb == None:
                field._pt_lsb = next_lsb
            elif isinstance(field._pt_lsb, Offset):
                field._pt_lsb = next_lsb + field._pt_lsb.value
            else:
                assert field._pt_lsb >= next_lsb, \
                    f"Field {field._pt_name} of {self._pt_name} specifies an " \
                    f"LSB ({field._pt_lsb}) that's out-of-order with the struct"
            next_lsb = (field._pt_lsb + field._pt_width)
        # Calculate the width of the struct
        if not self._pt_width:
            self._pt_width = max((
                (x._pt_width + x._pt_lsb) for x in self._pt_values()
            ))
