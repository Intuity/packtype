# Copyright 2023, Peter Birch, mailto:peter@intuity.io
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

import re

RGX_CAMEL = re.compile(r"([A-Z]+[a-z0-9]+)")


def snake_case(raw: str) -> str:
    """Convert a camel case string into snake case

    :param raw: The raw string to convert
    :returns:   A snake_case string
    """
    parts = filter(lambda x: len(x) > 0, RGX_CAMEL.split(raw))
    return "_".join(x.lower().strip("_") for x in parts)


def shouty_snake_case(raw: str) -> str:
    """Convert a lower case string into shouty snake case

    :param raw: The raw string to convert
    :returns:   A SHOUTY_SNAKE_CASE string
    """
    return snake_case(raw).upper()


def camel_case(raw: str) -> str:
    """Convert a snake case string into camel case

    :param raw: The raw string to convert
    :returns:   A CamelCase string
    """
    parts = sum([RGX_CAMEL.split(x) for x in raw.split("_")], [])
    return "".join(x.capitalize() for x in parts)


def underscore(raw: str) -> str:
    """Convert a dot separated string to underscore separation

    :param raw: Raw string to convert
    :returns:   Underscore separated string
    """
    return raw.strip().replace(".", "_")
