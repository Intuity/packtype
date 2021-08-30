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

from .constant import Constant
from .container import Container
from .enum import Enum
from .instance import Instance
from .struct import Struct
from .union import Union

class Package(Container):
    """ Package of different constants, enumerations, structs, and unions """

    def __init__(self, name, fields, desc=None):
        """ Initialise package with name and fields

        Args:
            name  : Name of the container
            fields: Dictionary of fields
            desc  : Optional description
        """
        # Perform container construction
        super().__init__(
            name, fields, desc=desc, legal=[Constant, Enum, Struct, Union],
            mutable=True
        )

