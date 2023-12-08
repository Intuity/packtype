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
from packtype import Package
from packtype.wrap import Registry

from ..fixtures import reset_registry

assert reset_registry


def test_registry():
    # Check that registry is empty
    assert len(list(Registry.query(Package))) == 0

    # Create a package
    @packtype.package()
    class PkgA:
        pass

    # Check that registry has one entry
    assert len(list(Registry.query(Package))) == 1
    assert list(Registry.query(Package))[0] is PkgA

    # Create a second package
    @packtype.package()
    class PkgB:
        pass

    # Check that registry has one entry
    assert len(list(Registry.query(Package))) == 2
    assert list(Registry.query(Package))[0] is PkgA
    assert list(Registry.query(Package))[1] is PkgB
