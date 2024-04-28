# Copyright 2024, Peter Birch, mailto:peter@intuity.io
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
