# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

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
    assert next(iter(Registry.query(Package))) is PkgA

    # Create a second package
    @packtype.package()
    class PkgB:
        pass

    # Check that registry has one entry
    assert len(list(Registry.query(Package))) == 2
    iterator = iter(Registry.query(Package))
    assert next(iterator) is PkgA
    assert next(iterator) is PkgB
