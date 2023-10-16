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

class Typedef(Container):
    """ A simple named fixed-width data structure """

    def __init__(self, width, name=None, desc=None):
        """ Initialise structure with name and fields

        Args:
            width: Bit width
            name : Optional name of the container
            desc : Optional description
        """
        super().__init__(name=name, width=width)
        # Sanity check width
        assert (width is None) or (isinstance(width, int) or width >= 0), \
            f"Width must be None or a positive integer, not '{width}'"
