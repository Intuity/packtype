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

from .assembly import Packing
from .package import Package
from .wrap import get_wrapper
from .constant import Constant
from .scalar import Scalar

package = get_wrapper(Package)

@package()
class TestPkg:
    "test doc"
    ABC: Constant[12] = 0
    DEF: Constant[16] = 1

    def test_func(self, abc):
        return abc + 123

@TestPkg.struct(width=64)
class Request:
    address: Scalar[32]
    length: Scalar[19]
    mode: Scalar[3]

@TestPkg.struct(packing=Packing.FROM_MSB)
class Outer:
    req: Request
    other: Scalar[2]

inst = TestPkg()

req = inst.Request()
out = inst.Outer()
print(int(out))

breakpoint()
