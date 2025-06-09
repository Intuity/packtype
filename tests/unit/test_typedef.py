# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Alias, Scalar

from ..fixtures import reset_registry

assert reset_registry


def test_typedef_scalar():
    @packtype.package()
    class TestPkg:
        Unsigned: Scalar[15]
        Signed: Scalar[12, True]

    unsigned = TestPkg.Unsigned()
    assert unsigned._pt_width == 15
    assert not unsigned._pt_signed
    signed = TestPkg.Signed()
    assert signed._pt_width == 12
    assert signed._pt_signed


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
