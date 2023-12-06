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

from random import randint

import pytest

import packtype
from packtype import Scalar

def test_union_scalars():
    """ Construct a basic union between equally sized scalars """
    width = randint(1, 32)
    @packtype.union()
    class MyUnion:
        var_a : Scalar(width=width, desc="Description A")
        var_b : Scalar(width=width, desc="Description B")
        var_c : Scalar(width=width, desc="Description C")
    assert list(MyUnion._pt_keys()) == ["var_a", "var_b", "var_c"]
    assert MyUnion.var_a._pt_width == width
    assert MyUnion.var_b._pt_width == width
    assert MyUnion.var_c._pt_width == width

def test_union_bad_scalars():
    """ Attempt to construct a union with different scalar sizes """
    widths = [randint(1, 32) for _ in range(3)]
    with pytest.raises(AssertionError) as excinfo:
        @packtype.union()
        class MyUnion:
            var_a : Scalar(width=widths[0], desc="Description A")
            var_b : Scalar(width=widths[1], desc="Description B")
            var_c : Scalar(width=widths[2], desc="Description C")
    assert f"Unmatched widths of fields in union MyUnion: {widths}"

def test_union_structs():
    """ Construct a basic union between equally sized scalars """
    @packtype.struct()
    class StructA:
        field_a : Scalar(width= 5, desc="Description A")
        field_b : Scalar(width=10, desc="Description B")
        field_c : Scalar(width=20, desc="Description C")
    @packtype.struct()
    class StructB:
        field_a : Scalar(width=15, desc="Description A")
        field_b : Scalar(width=15, desc="Description B")
        field_c : Scalar(width= 5, desc="Description C")
    @packtype.struct()
    class StructC:
        field_a : Scalar(width=18, desc="Description A")
        field_b : Scalar(width=11, desc="Description B")
        field_c : Scalar(width= 6, desc="Description C")
    @packtype.union()
    class MyUnion:
        str_a : StructA(desc="Description A")
        str_b : StructB(desc="Description B")
        str_c : StructC(desc="Description C")
    assert MyUnion._pt_width       == 35
    assert MyUnion.str_a._pt_width == 35
    assert MyUnion.str_b._pt_width == 35
    assert MyUnion.str_c._pt_width == 35

def test_union_structs():
    """ Attempt to construct a union between mismatched structs """
    @packtype.struct()
    class StructA:
        field_a : Scalar(width= 5, desc="Description A")
        field_b : Scalar(width=10, desc="Description B")
        field_c : Scalar(width=18, desc="Description C")
    @packtype.struct()
    class StructB:
        field_a : Scalar(width=17, desc="Description A")
        field_b : Scalar(width=15, desc="Description B")
        field_c : Scalar(width= 5, desc="Description C")
    @packtype.struct()
    class StructC:
        field_a : Scalar(width=18, desc="Description A")
        field_b : Scalar(width=11, desc="Description B")
        field_c : Scalar(width= 6, desc="Description C")
    with pytest.raises(AssertionError) as excinfo:
        @packtype.union()
        class BadUnion:
            str_a : StructA(desc="Description A")
            str_b : StructB(desc="Description B")
            str_c : StructC(desc="Description C")
    assert f"Unmatched widths of fields in union BadUnion: [33, 37, 35]"
