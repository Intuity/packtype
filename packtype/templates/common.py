# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import re

RGX_CAMEL = re.compile(r"([A-Z]+[a-z0-9]+)")


def snake_case(raw: str) -> str:
    """Convert a camel case string into snake case

    :param raw: The raw string to convert
    :returns:   A snake_case string
    """
    parts = filter(lambda x: len(x) > 0, RGX_CAMEL.split(raw))
    return "_".join(x.lower().rstrip("_") for x in parts)


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
