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

import pytest
import packtype
from packtype import Constant, EnumMode
from packtype.enum import EnumError

from ..fixtures import reset_registry

assert reset_registry


def test_enum_auto_indexed():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum()
    class TestEnum:
        A: Constant
        B: Constant
        C: Constant

    inst = TestEnum()
    assert int(inst.A) == 0
    assert int(inst.B) == 1
    assert int(inst.C) == 2


def test_enum_auto_onehot():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.ONE_HOT)
    class TestEnum:
        A: Constant
        B: Constant
        C: Constant

    inst = TestEnum()
    assert int(inst.A) == 1
    assert int(inst.B) == 2
    assert int(inst.C) == 4


def test_enum_auto_gray():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.GRAY)
    class TestEnum:
        A: Constant
        B: Constant
        C: Constant
        D: Constant

    inst = TestEnum()
    assert int(inst.A) == 0
    assert int(inst.B) == 1
    assert int(inst.C) == 3
    assert int(inst.D) == 2


def test_enum_manual_indexed():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum()
    class TestEnum:
        A: Constant = 2
        B: Constant = 3
        C: Constant = 4

    inst = TestEnum()
    assert int(inst.A) == 2
    assert int(inst.B) == 3
    assert int(inst.C) == 4


def test_enum_manual_onehot():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.ONE_HOT)
    class TestEnum:
        A: Constant = 1
        B: Constant = 4
        C: Constant = 16

    inst = TestEnum()
    assert int(inst.A) == 1
    assert int(inst.B) == 4
    assert int(inst.C) == 16


def test_enum_manual_gray():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.GRAY)
    class TestEnum:
        A: Constant = 0
        B: Constant = 1
        C: Constant = 3
        D: Constant = 2

    inst = TestEnum()
    assert int(inst.A) == 0
    assert int(inst.B) == 1
    assert int(inst.C) == 3
    assert int(inst.D) == 2


def test_enum_bad_one_hot():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.ONE_HOT)
    class TestEnum:
        A: Constant = 1
        B: Constant = 2
        C: Constant = 3

    with pytest.raises(EnumError) as e:
        TestEnum()

    assert str(e.value) == "Enum entry C has value 3 that is not one-hot"


def test_enum_bad_gray():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.GRAY)
    class TestEnum:
        A: Constant = 0
        B: Constant = 1
        C: Constant = 2
        D: Constant = 3

    with pytest.raises(EnumError) as e:
        TestEnum()

    assert str(e.value) == (
        "Enum entry C has value 2 that does not conform to the expected Gray "
        "code value of 3"
    )


def test_enum_bad_repeated():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.INDEXED)
    class TestEnum:
        A: Constant = 0
        B: Constant = 1
        C: Constant = 2
        D: Constant = 2

    with pytest.raises(EnumError) as e:
        TestEnum()

    assert str(e.value) == (
        "Enum entry D has value 2 that appears more than once in the enumeration"
    )


def test_enum_bad_oversized():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(mode=EnumMode.INDEXED, width=2)
    class TestEnum:
        A: Constant
        B: Constant
        C: Constant
        D: Constant
        E: Constant

    with pytest.raises(EnumError) as e:
        TestEnum()

    assert str(e.value) == (
        "Enum entry E has value 4 that cannot be encoded in a bit width of 2"
    )


def test_enum_prefix():
    @packtype.package()
    class TestPkg:
        pass

    @TestPkg.enum(prefix="BLAH")
    class TestEnum:
        A: Constant
        B: Constant
        C: Constant

    assert TestEnum()._pt_prefix == "BLAH"
