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

from random import choice, randint
from string import ascii_letters

def random_str(max_len, min_len=1, avoid=None, spaces=False):
    """ Generate a random string of the specified length.

    Args:
        max_len: Maximum length of string
        min_len: Minimum length of string (default: 1)
        avoid  : Optional list of strings to avoid (default: None)
        spaces : Whether to include spaces (default: False)

    Returns: Random ASCII string
    """
    def rand_ascii(min_len, max_len):
        return "".join([
            choice(ascii_letters) for _x in range(randint(min_len, max_len))
        ])
    while True:
        r_str = ""
        if spaces:
            while len(r_str) < min_len:
                r_str += rand_ascii(1, min(6, max_len - len(r_str)))
                if len(r_str) < (min_len - 1): r_str += " "
        else:
            r_str = rand_ascii(min_len, max_len)
        if not isinstance(avoid, list) or r_str not in avoid:
            return r_str
