# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Scalar


@packtype.package()
class DemoPkg:
    pass


@DemoPkg.struct()
class TestStruct:
    a: Scalar[8]
    b: Scalar[8]
    e: Scalar[32]
    c: Scalar[8]
    d: Scalar[8]
