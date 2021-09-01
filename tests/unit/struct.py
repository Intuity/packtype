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

from packtype.container import Container
from packtype.constant import Constant
from packtype.instance import Instance
from random import randint

import pytest

import packtype
from packtype import Offset, Scalar

from .common import random_str

def test_struct_scalar():
    """ Basic struct containing scalars """
    width_a, width_b, width_c = randint(1, 10), randint(1, 10), randint(1, 10)
    desc_a,  desc_b,  desc_c  = random_str(30), random_str(30), random_str(30)
    @packtype.struct()
    class MyStruct:
        field_a : Scalar(width=width_a, desc=desc_a)
        field_b : Scalar(width=width_b, desc=desc_b)
        field_c : Scalar(width=width_c, desc=desc_c)
    assert MyStruct.field_a._pt_width == width_a
    assert MyStruct.field_b._pt_width == width_b
    assert MyStruct.field_c._pt_width == width_c
    assert MyStruct.field_a._pt_desc == desc_a
    assert MyStruct.field_b._pt_desc == desc_b
    assert MyStruct.field_c._pt_desc == desc_c
    assert MyStruct.field_a._pt_lsb == 0
    assert MyStruct.field_a._pt_msb == width_a - 1
    assert MyStruct.field_a._pt_mask == (1 << width_a) - 1
    assert MyStruct.field_b._pt_lsb == width_a
    assert MyStruct.field_b._pt_msb == width_a + width_b - 1
    assert MyStruct.field_b._pt_mask == (1 << width_b) - 1
    assert MyStruct.field_c._pt_lsb == width_a + width_b
    assert MyStruct.field_c._pt_msb == width_a + width_b + width_c - 1
    assert MyStruct.field_c._pt_mask == (1 << width_c) - 1
    assert MyStruct._pt_width == width_a + width_b + width_c

def test_struct_enum():
    """ Struct containing enumerations """
    @packtype.enum()
    class EnumA:
        VALUE_A : Constant(desc="Description A")
        VALUE_B : Constant(desc="Description B")
        VALUE_C : Constant(desc="Description C")
    @packtype.enum(mode="ONEHOT")
    class EnumB:
        VALUE_D : Constant(desc="Description D")
        VALUE_E : Constant(desc="Description E")
        VALUE_F : Constant(desc="Description F")
    @packtype.struct()
    class MyStruct:
        enum_a : EnumA(desc="Enumerated item A")
        enum_b : EnumB(desc="Enumerated item B")
    assert MyStruct.enum_a.VALUE_A.value == 0
    assert MyStruct.enum_a.VALUE_B.value == 1
    assert MyStruct.enum_a.VALUE_C.value == 2
    assert MyStruct.enum_b.VALUE_D.value == 1
    assert MyStruct.enum_b.VALUE_E.value == 2
    assert MyStruct.enum_b.VALUE_F.value == 4
    assert MyStruct.enum_a._pt_lsb == 0
    assert MyStruct.enum_a._pt_msb == EnumA._pt_width - 1
    assert MyStruct.enum_a._pt_mask == (1 << EnumA._pt_width) - 1
    assert MyStruct.enum_b._pt_lsb == EnumA._pt_width
    assert MyStruct.enum_b._pt_msb == EnumA._pt_width + EnumB._pt_width - 1
    assert MyStruct.enum_b._pt_mask == (1 << EnumB._pt_width) - 1

def test_struct_nested():
    """ Struct containing other structs """
    widths = [randint(1, 10) for _ in range(9)]
    descs  = [random_str(30) for _ in range(9)]
    # Child struct A
    @packtype.struct()
    class SubStructA:
        field_a : Scalar(width=widths[0], desc=descs[0])
        field_b : Scalar(width=widths[1], desc=descs[1])
        field_c : Scalar(width=widths[2], desc=descs[2])
    # Child struct B
    @packtype.struct()
    class SubStructB:
        field_a : Scalar(width=widths[3], desc=descs[3])
        field_b : Scalar(width=widths[4], desc=descs[4])
        field_c : Scalar(width=widths[5], desc=descs[5])
    # Parent struct
    @packtype.struct()
    class Parent:
        field_a : Scalar(width=widths[6], desc=descs[6])
        child_a : SubStructA(desc="Child A")
        field_b : Scalar(width=widths[7], desc=descs[7])
        child_b : SubStructB(desc="Child B")
        field_c : Scalar(width=widths[8], desc=descs[8])
    # Tests
    assert Parent.field_a._pt_width == widths[6]
    assert Parent.field_b._pt_width == widths[7]
    assert Parent.field_c._pt_width == widths[8]
    assert Parent.child_a.field_a._pt_width == widths[0]
    assert Parent.child_a.field_b._pt_width == widths[1]
    assert Parent.child_a.field_c._pt_width == widths[2]
    assert Parent.child_b.field_a._pt_width == widths[3]
    assert Parent.child_b.field_b._pt_width == widths[4]
    assert Parent.child_b.field_c._pt_width == widths[5]
    assert Parent.field_a._pt_desc == descs[6]
    assert Parent.field_b._pt_desc == descs[7]
    assert Parent.field_c._pt_desc == descs[8]
    assert Parent.child_a.field_a._pt_desc == descs[0]
    assert Parent.child_a.field_b._pt_desc == descs[1]
    assert Parent.child_a.field_c._pt_desc == descs[2]
    assert Parent.child_b.field_a._pt_desc == descs[3]
    assert Parent.child_b.field_b._pt_desc == descs[4]
    assert Parent.child_b.field_c._pt_desc == descs[5]
    assert Parent.field_a._pt_lsb == 0
    assert Parent.field_a._pt_msb == widths[6] - 1
    assert Parent.field_a._pt_mask == (1 << widths[6]) - 1
    assert Parent.child_a._pt_lsb == widths[6]
    assert Parent.child_a._pt_msb == widths[6] + SubStructA._pt_width - 1
    assert Parent.child_a._pt_mask == (1 << SubStructA._pt_width) - 1
    assert Parent.field_b._pt_lsb == widths[6] + SubStructA._pt_width
    assert Parent.field_b._pt_msb == widths[6] + SubStructA._pt_width + widths[7] - 1
    assert Parent.field_b._pt_mask == (1 << widths[7]) - 1
    assert Parent.child_b._pt_lsb == widths[6] + SubStructA._pt_width + widths[7]
    assert Parent.child_b._pt_msb == widths[6] + SubStructA._pt_width + widths[7] + SubStructB._pt_width - 1
    assert Parent.child_b._pt_mask == (1 << SubStructB._pt_width) - 1
    assert Parent.field_c._pt_lsb == (
        widths[6] + SubStructA._pt_width + widths[7] + SubStructB._pt_width
    )
    assert Parent.field_c._pt_msb == (
        widths[6] + SubStructA._pt_width + widths[7] + SubStructB._pt_width +
        widths[8] - 1
    )
    assert Parent.field_c._pt_mask == (1 << widths[8]) - 1
    assert Parent._pt_width == (
        sum(widths[6:]) + SubStructA._pt_width + SubStructB._pt_width
    )

def test_struct_offset():
    """ Ensure structures support absolute and relative offset fields """
    abs_off, rel_off = randint(1, 8), randint(1, 8)
    width_a, width_b = randint(1, 8), randint(1, 8)
    @packtype.struct()
    class MyStruct:
        field_a : Scalar(width=width_a, lsb=abs_off)
        field_b : Scalar(width=width_b, lsb=Offset(rel_off))
    assert MyStruct.field_a._pt_lsb == abs_off
    assert MyStruct.field_b._pt_lsb == abs_off + width_a + rel_off
    assert MyStruct._pt_width == abs_off + width_a + rel_off + width_b

def test_struct_bad_lsb():
    """ Attempt to create a struct with a clashing LSB value """
    width_a, width_b = randint(2, 10), randint(1, 10)
    lsb_b            = width_a // 2
    with pytest.raises(AssertionError) as excinfo:
        @packtype.struct()
        class BadStruct:
            field_a : Scalar(width=width_a)
            field_b : Scalar(width=width_b, lsb=lsb_b)
    assert f"Field field_b of BadStruct specifies an out-of-order LSB ({lsb_b})"

def test_struct_bad_field():
    """ Attempt to create a struct with a bad field type """
    # Test a naked object
    with pytest.raises(AssertionError) as excinfo:
        @packtype.struct()
        class MyStruct:
            field_a : Scalar(width=1, desc="Description of A")
            field_b : Scalar(width=2, desc="Description of B")
            field_c : Scalar(width=3, desc="Description of C")
            field_d : Constant(value=4, width=3)
    assert (
        "Field 'field_d' of MyStruct must be within: Enum, Struct, Union, Scalar"
        in str(excinfo.value)
    )
    # Test an object instance
    class BadContainer(Container): pass
    with pytest.raises(AssertionError) as excinfo:
        @packtype.struct()
        class MyStruct:
            field_a : Scalar(width=1, desc="Description of A")
            field_b : Scalar(width=2, desc="Description of B")
            field_c : Scalar(width=3, desc="Description of C")
            field_d : Instance(BadContainer("blah", {}))
    assert (
        "Field 'field_d' of MyStruct must be within: Enum, Struct, Union, Scalar"
        in str(excinfo.value)
    )

def test_struct_instance():
    """ Create an instance of a struct """
    # Define the struct
    widths = [randint(1, 10) for _ in range(3)]
    descs  = [random_str(30) for _ in range(3)]
    @packtype.struct()
    class MyStruct:
        field_a : Scalar(width=widths[0], desc=descs[0])
        field_b : Scalar(width=widths[1], desc=descs[1])
        field_c : Scalar(width=widths[2], desc=descs[2])
    # Create the instance
    inst = MyStruct(desc="Instance of MyStruct")
    # Try setting the name of the struct to a non-string
    val = randint(1, 10)
    with pytest.raises(AssertionError) as excinfo: inst._pt_name = val
    assert f"Name must be a string: {val}" in str(excinfo.value)
    # Set the name
    inst._pt_name = "inst"
    # Try renaming the instance
    with pytest.raises(AssertionError) as excinfo: inst._pt_name = random_str(30)
    assert f"Trying to change name of instance inst"
    # Set the description
    assert inst._pt_name == "inst"
    assert inst._pt_desc == "Instance of MyStruct"
    # Iterate through fields
    for idx, field in enumerate(inst._pt_values()):
        assert field._pt_width == widths[idx]
        assert field._pt_desc  == descs[idx]
