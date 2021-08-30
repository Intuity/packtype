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
import re

def opt_desc(obj, delim):
    """ Generate a description comment when a description is provided.

    Args:
        obj  : A packtype object
        delim: The comment delimiter for the active language

    Returns: A delimited comment string containing the description
    """
    return f"{delim} {obj.desc}" if obj.desc else ""

RGX_CAMEL = re.compile(r"([A-Z]+[a-z0-9]+)")
def snake_case(raw):
    """ Convert a camel case string into snake case

    Args:
        raw: The raw string to convert

    Returns: A snake_case string
    """
    parts = filter(lambda x: len(x) > 0, RGX_CAMEL.split(raw))
    return "_".join([x.lower() for x in parts])

# ==============================================================================
# Language Specific Helpers
# ==============================================================================

def c_obj_type(obj):
    """ Generate a C type which is sufficiently large enough to hold a value

    Args:
        obj: A packtype object

    Returns: A string of the type
    """
    sizing = None
    signed = (hasattr(obj, "_pt_signed") and obj._pt_signed)
    if obj._pt_width <= 16:
        sizing = int(math.ceil(obj._pt_width / 8)) * 8
    else:
        sizing = int(math.ceil(obj._pt_width / 32)) * 32
    assert sizing != None, f"Failed to resolve size for: {obj}"
    return f"{'' if signed else 'u'}int{sizing}_t"
