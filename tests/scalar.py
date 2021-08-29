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

from packtype import Scalar

from .common import random_str

def test_scalar_default():
    """ Test a scalar's default behaviour """
    var = Scalar()
    assert var._pt_width  == 32
    assert var._pt_signed == False
    assert var._pt_lsb    == None
    assert var._pt_name   == None
    assert var._pt_desc   == None

def test_scalar_init():
    """ Create a scalar and check that properties are registered """
    width  = randint(1, 128)
    signed = choice((True, False))
    lsb    = randint(0, width-1)
    name   = random_str(10)
    desc   = random_str(20)
    var = Scalar(width=width, signed=signed, lsb=lsb, name=name, desc=desc)
    assert var._pt_width  == width
    assert var._pt_signed == signed
    assert var._pt_lsb    == lsb
    assert var._pt_name   == name
    assert var._pt_desc   == desc

def test_scalar_bad_width():
    """ A zero or negative width should be prohibited """
    # Check that a zero width is prohibited
    with pytest.raises(AssertionError) as excinfo:
        Scalar(width=0)
    assert "Width must be a positive integer: 0" in str(excinfo.value)
    # Check that a negative width is prohibited
    neg_width = -1 * randint(1, 1000)
    with pytest.raises(AssertionError) as excinfo:
        Scalar(width=neg_width)
    assert f"Width must be a positive integer: {neg_width}" in str(excinfo.value)

def test_scalar_bad_signedness():
    """ A value other than True/False for signedness should be prohibited """
    # Check that an integer is prohibited
    integer = randint(-1000, 1000)
    with pytest.raises(AssertionError) as excinfo:
        Scalar(signed=integer)
    assert f"Signedness must be either True or False: {integer}" in str(excinfo.value)
    # Check that a string is prohibited
    string = random_str(10)
    with pytest.raises(AssertionError) as excinfo:
        Scalar(signed=string)
    assert f"Signedness must be either True or False: {string}" in str(excinfo.value)

def test_scalar_bad_lsb():
    """ A negative LSB should be prohibited """
    # Test bad LSB on construction
    neg_lsb = -1 * randint(1, 1000)
    with pytest.raises(AssertionError) as excinfo:
        Scalar(lsb=neg_lsb)
    assert f"Least significant bit must be None or an integer: {neg_lsb}" in str(excinfo.value)
    # Test bad LSB after construction
    neg_lsb = -1 * randint(1, 1000)
    var     = Scalar()
    with pytest.raises(AssertionError) as excinfo:
        var._pt_lsb = neg_lsb
    assert f"LSB must be a positive integer: {neg_lsb}" in str(excinfo.value)

def test_scalar_bad_name():
    """ A non-string name should be prohibited """
    # Check that an integer is prohibited
    # - During construction
    integer = randint(-1000, 1000)
    with pytest.raises(AssertionError) as excinfo:
        Scalar(name=integer)
    assert f"Name must be None or a string: {integer}" in str(excinfo.value)
    # - After construction
    integer = randint(-1000, 1000)
    var     = Scalar()
    with pytest.raises(AssertionError) as excinfo:
        var._pt_name = integer
    assert f"Name must be a string: {integer}" in str(excinfo.value)
    # Check that a boolean is prohibited
    # - During construction
    boolean = choice((True, False))
    with pytest.raises(AssertionError) as excinfo:
        Scalar(name=boolean)
    assert f"Name must be None or a string: {boolean}" in str(excinfo.value)
    # - After construction
    boolean = choice((True, False))
    var     = Scalar()
    with pytest.raises(AssertionError) as excinfo:
        var._pt_name = boolean
    assert f"Name must be a string: {boolean}" in str(excinfo.value)

def test_scalar_bad_desc():
    """ A non-string description should be prohibited """
    # Check that an integer is prohibited
    # - During construction
    integer = randint(-1000, 1000)
    with pytest.raises(AssertionError) as excinfo:
        Scalar(desc=integer)
    assert f"Description must be None or a string: {integer}" in str(excinfo.value)
    # - After construction
    integer = randint(-1000, 1000)
    var     = Scalar()
    with pytest.raises(AssertionError) as excinfo:
        var._pt_desc = integer
    assert f"Description must be a string: {integer}" in str(excinfo.value)
    # Check that a string is prohibited
    boolean = choice((True, False))
    with pytest.raises(AssertionError) as excinfo:
        Scalar(desc=boolean)
    assert f"Description must be None or a string: {boolean}" in str(excinfo.value)
    # - After construction
    boolean = choice((True, False))
    var     = Scalar()
    with pytest.raises(AssertionError) as excinfo:
        var._pt_desc = boolean
    assert f"Description must be a string: {boolean}" in str(excinfo.value)

def test_scalar_alter_lsb():
    """ Try altering the LSB after it was set """
    # Set the LSB in the initialisation, then alter it
    name = random_str(10)
    lsb  = randint(0, 31)
    var  = Scalar(name=name, lsb=lsb)
    with pytest.raises(AssertionError) as excinfo:
        var._pt_lsb = randint(32, 63)
    assert f"Trying to alter LSB of scalar {name}" in str(excinfo.value)
    assert var._pt_lsb == lsb
    # Set the LSB after initialisation, then alter it
    name = random_str(10)
    lsb  = randint(0, 31)
    var  = Scalar(name=name)
    var._pt_lsb = lsb
    with pytest.raises(AssertionError) as excinfo:
        var._pt_lsb = randint(32, 63)
    assert f"Trying to alter LSB of scalar {name}" in str(excinfo.value)
    assert var._pt_lsb == lsb

def test_scalar_alter_name():
    """ Try altering the name after it was set """
    # Set the LSB in the initialisation, then alter it
    name = random_str(10)
    var  = Scalar(name=name)
    with pytest.raises(AssertionError) as excinfo:
        var._pt_name = random_str(10)
    assert f"Trying to alter name of scalar {name}" in str(excinfo.value)
    assert var._pt_name == name
    # Set the LSB after initialisation, then alter it
    name = random_str(10)
    var  = Scalar()
    var._pt_name = name
    with pytest.raises(AssertionError) as excinfo:
        var._pt_name = random_str(10)
    assert f"Trying to alter name of scalar {name}" in str(excinfo.value)
    assert var._pt_name == name

def test_scalar_alter_desc():
    """ Try altering the description after it was set """
    # Set the LSB in the initialisation, then alter it
    name = random_str(10)
    desc = random_str(10)
    var  = Scalar(name=name, desc=desc)
    with pytest.raises(AssertionError) as excinfo:
        var._pt_desc = random_str(10)
    assert f"Trying to alter description of scalar {name}" in str(excinfo.value)
    assert var._pt_desc == desc
    # Set the LSB after initialisation, then alter it
    name = random_str(10)
    desc = random_str(10)
    var  = Scalar(name=name)
    var._pt_desc = desc
    with pytest.raises(AssertionError) as excinfo:
        var._pt_desc = random_str(10)
    assert f"Trying to alter description of scalar {name}" in str(excinfo.value)
    assert var._pt_desc == desc
