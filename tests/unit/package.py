# Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk
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

from random import randint, choice

import pytest

import packtype
from packtype import Constant, Scalar

from .common import random_str

def test_package_desc():
    """ Set and try to alter a description of a package """
    @packtype.package()
    class TestPackage:
        pass
    desc = random_str(30)
    TestPackage._pt_desc = desc
    assert TestPackage._pt_desc == desc
    with pytest.raises(AssertionError) as excinfo:
        TestPackage._pt_desc = random_str(30)
    assert "Trying to alter description of TestPackage" == str(excinfo.value)
    assert TestPackage._pt_desc == desc

def test_package_constants():
    """ Check that a package can hold constants """
    values = [randint(1, 1000) for _ in range(3)]
    descs  = [random_str(30) for _ in range(3)]
    @packtype.package()
    class TestPackage:
        """ Description of the test package """
        CONST_A : Constant(desc=descs[0]) = values[0]
        CONST_B : Constant(desc=descs[1]) = values[1]
        CONST_C : Constant(desc=descs[2]) = values[2]
    assert TestPackage._pt_desc == "Description of the test package"
    assert TestPackage.CONST_A.value == values[0]
    assert TestPackage.CONST_B.value == values[1]
    assert TestPackage.CONST_C.value == values[2]
    assert TestPackage.CONST_A._pt_desc == descs[0]
    assert TestPackage.CONST_B._pt_desc == descs[1]
    assert TestPackage.CONST_C._pt_desc == descs[2]

def test_package_members():
    """ Associate other type definitions with a package """
    @packtype.package()
    class TestPackage:
        pass
    @packtype.enum(package=TestPackage)
    class TestEnum:
        VALUE_A : Constant() = 0
        VALUE_B : Constant() = 1
        VALUE_C : Constant() = 2
    @packtype.struct(package=TestPackage)
    class TestStruct:
        field_a : Scalar()
        field_b : Scalar()
        field_c : Scalar()
    assert TestPackage.TestEnum == TestEnum
    assert TestPackage.TestStruct == TestStruct
    assert TestPackage._pt_fields == {
        "TestEnum": TestEnum, "TestStruct": TestStruct,
    }

def test_package_bad_member():
    """ Try accessing a non-existent member """
    @packtype.package()
    class TestPackage:
        pass
    with pytest.raises(AttributeError) as excinfo:
        assert TestPackage.blah
    assert "'Package' object has no attribute 'blah'" == str(excinfo.value)
