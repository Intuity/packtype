# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
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


def clog2(x: int) -> int:
    """Calculate the ceiling of the base-2 logarithm of x."""
    assert x > 0, "Input must be a positive integer."
    return math.ceil(math.log2(x))


def width(ptype: type[Base]) -> int:
    """Get the width of a Packtype definition"""
    if isinstance(ptype, Base):
        return ptype._pt_width
    elif issubclass(ptype, Base):
        return ptype._PT_WIDTH
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")
