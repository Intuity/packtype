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

from packtype import Constant

from .common import random_str

def test_constant_default():
    """ Test a constants's default behaviour """
    var = Constant()
    assert var.value      == None
    assert var.width      == 32
    assert var._pt_width  == 32
    assert var.signed     == False
    assert var._pt_signed == False
    assert var.name       == None
    assert var._pt_name   == None
    assert var.desc       == None
    assert var._pt_desc   == None

def test_constant_init():
    """ Create a constant and check the properties are registered """
    width  = randint(1, 64)
    signed = choice((True, False))
    name   = random_str(10)
    desc   = random_str(30)
    value  = (
        randint(-1 * (1 << (width - 1)), (1 << (width-1)) - 1) if signed else
        randint(0, (1 << width) - 1)
    )
    var = Constant(value=value, width=width, signed=signed, name=name, desc=desc)
    assert var.value      == value
    assert int(var)       == value
    assert var.width      == width
    assert var._pt_width  == width
    assert var.signed     == signed
    assert var._pt_signed == signed
    assert var.name       == name
    assert var._pt_name   == name
    assert var.desc       == desc
    assert var._pt_desc   == desc

def test_constant_alter_desc():
    """ Create a constant, then alter the description """
    name = random_str(10)
    desc = random_str(30)
    var  = Constant(value=randint(0, 1000), name=name)
    var._pt_desc = desc
    assert var._pt_desc == desc
    with pytest.raises(AssertionError) as excinfo:
        var._pt_desc = random_str(30)
    assert f"Trying to alter description of constant {name}" == str(excinfo.value)
    assert var._pt_desc == desc

def test_constant_bad_value():
    """ Try creating a constant with a bad value """
    # Try creating a constant with a string
    val = random_str(10)
    with pytest.raises(AssertionError) as excinfo: Constant(value=val)
    assert f"Value must be None or an integer: {val}" in str(excinfo.value)
    # Try creating an unsigned constant with a negative value
    neg_val = -1 * randint(1, 1000)
    with pytest.raises(AssertionError) as excinfo: Constant(value=neg_val)
    assert f"Value {neg_val} is outside of an unsigned 32 bit range" in str(excinfo.value)
    # Try creating an unsigned constant with an out-of-range value
    val = randint(16, 32)
    with pytest.raises(AssertionError) as excinfo: Constant(width=4, value=val)
    assert f"Value {val} is outside of an unsigned 4 bit range" in str(excinfo.value)
    # Try creating a signed constant with an out-of-range +'ve value
    val = randint(128, 256)
    with pytest.raises(AssertionError) as excinfo:
        Constant(width=8, signed=True, value=val)
    assert f"Value {val} is outside of a signed 8 bit range" in str(excinfo.value)
    # Try creating a signed constant with an out-of-range -'ve value
    val = -1 * randint(129, 256)
    with pytest.raises(AssertionError) as excinfo:
        Constant(width=8, signed=True, value=val)
    assert f"Value {val} is outside of a signed 8 bit range" in str(excinfo.value)

def test_constant_bad_desc():
    """ Create a constant, then alter the description """
    name = random_str(10)
    var  = Constant(value=randint(0, 1000), name=name)
    with pytest.raises(AssertionError) as excinfo:
        var._pt_desc = 1234
    assert "Description must be a string: 1234" == str(excinfo.value)
