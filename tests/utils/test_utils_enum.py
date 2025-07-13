# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Constant, utils

from ..fixtures import reset_registry

assert reset_registry


def test_utils_enum_get_entries():
    @packtype.package()
    class PackageA:
        pass

    @PackageA.enum()
    class EnumA:
        A: Constant
        B: Constant

    entries = list(utils.enum.get_entries(EnumA))
    assert entries[0][0] == "A"
    assert entries[0][1] == 0
    assert entries[1][0] == "B"
    assert entries[1][1] == 1
