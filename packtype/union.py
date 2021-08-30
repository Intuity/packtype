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
from .scalar import Scalar
from .struct import Struct

class Union(Container):
    """ Packed data structure formed of other structures or unions """

    def __init__(self, name, fields, desc=None):
        """ Initialise union with name and fields

        Args:
            name  : Name of the container
            fields: Dictionary of fields
            desc  : Optional description
        """
        # Perform container construction
        super().__init__(name, fields, desc=desc, legal=[Scalar, Struct, Union])
        # Check all fields are the same width
        widths = [x._pt_width for x in self._pt_values()]
        assert len(set(widths)) == 1, \
            f"Unmatched widths of fields in union {self._pt_name}: {widths}"
        # Calculate the width
        self._pt_width = next((x._pt_width for x in self._pt_values()))
