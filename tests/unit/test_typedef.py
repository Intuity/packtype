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

import packtype
from packtype import Alias, Scalar

from ..fixtures import reset_registry

assert reset_registry


def test_typedef_scalar():
    @packtype.package()
    class TestPkg:
        MyType: Scalar[15]

    inst = TestPkg.MyType()
    assert inst._pt_width == 15


def test_typedef_alias():
    @packtype.package()
    class PkgA:
        pass

    @PkgA.struct()
    class Header:
        address: Scalar[16]
        length: Scalar[8]

    @packtype.package()
    class PkgB:
        MyAlias: Alias[Header]

    assert PkgB().MyAlias._PT_ALIAS is Header
    assert issubclass(PkgB().MyAlias, Alias)
    inst = PkgB().MyAlias()
    assert isinstance(inst, Header)
