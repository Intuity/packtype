# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Constant, Scalar


@packtype.package()
class OtherPkg:
    pass


@OtherPkg.enum()
class Access:
    NOP: Constant
    READ: Constant
    WRITE: Constant


@packtype.package()
class TestPkg:
    """Testing a complete package definition"""

    # Constants
    DATA_W: Constant = 32
    ADDR_W: Constant = 16
    SIZE_W: Constant = 8

    # Typedefs
    Data: Scalar[DATA_W]
    Addr: Scalar[ADDR_W]
    Size: Scalar[SIZE_W]


@TestPkg.struct(width=TestPkg.DATA_W)
class Header:
    address: TestPkg.Addr
    length: TestPkg.Size
    access: Access
    misc: Scalar[2]


@TestPkg.union()
class Packet:
    header: Header
    payload: TestPkg.Data
