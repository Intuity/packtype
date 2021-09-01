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

import pytest

import packtype
from packtype import Constant

def test_enum_idx_explicit():
    """ Check behaviour of an explicitly valued indexed enumeration """
    @packtype.enum()
    class DummyEnum:
        """ Test description 12345 """
        KEY_A : Constant(desc="Description A") = 0
        KEY_B : Constant(desc="Description B") = 1
        KEY_C : Constant(desc="Description C") = 2
    assert DummyEnum._pt_desc == "Test description 12345"
    assert DummyEnum._pt_mode == "INDEXED"
    assert DummyEnum.KEY_A.name == "KEY_A"
    assert DummyEnum.KEY_B.name == "KEY_B"
    assert DummyEnum.KEY_C.name == "KEY_C"
    assert DummyEnum.KEY_A.desc == "Description A"
    assert DummyEnum.KEY_B.desc == "Description B"
    assert DummyEnum.KEY_C.desc == "Description C"
    assert DummyEnum.KEY_A.value == 0
    assert DummyEnum.KEY_B.value == 1
    assert DummyEnum.KEY_C.value == 2
    assert DummyEnum._pt_width == 2

def test_enum_idx_auto():
    """ Check behaviour of an auto-valued indexed enumeration """
    @packtype.enum()
    class DummyEnum:
        """ Test description 12345 """
        KEY_A : Constant(desc="Description A") # 0
        KEY_B : Constant(desc="Description B") # 1
        KEY_C : Constant(desc="Description C") # 2
        KEY_D : Constant(desc="Description D") = 5
        KEY_E : Constant(desc="Description E") # 6
    assert DummyEnum._pt_desc == "Test description 12345"
    assert DummyEnum._pt_mode == "INDEXED"
    assert DummyEnum.KEY_A.name == "KEY_A"
    assert DummyEnum.KEY_B.name == "KEY_B"
    assert DummyEnum.KEY_C.name == "KEY_C"
    assert DummyEnum.KEY_D.name == "KEY_D"
    assert DummyEnum.KEY_E.name == "KEY_E"
    assert DummyEnum.KEY_A.desc == "Description A"
    assert DummyEnum.KEY_B.desc == "Description B"
    assert DummyEnum.KEY_C.desc == "Description C"
    assert DummyEnum.KEY_D.desc == "Description D"
    assert DummyEnum.KEY_E.desc == "Description E"
    assert DummyEnum.KEY_A.value == 0
    assert DummyEnum.KEY_B.value == 1
    assert DummyEnum.KEY_C.value == 2
    assert DummyEnum.KEY_D.value == 5
    assert DummyEnum.KEY_E.value == 6
    assert DummyEnum._pt_width == 3

def test_enum_idx_bad_value():
    """ Check that an indexed enumeration detects negative values """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum()
        class BadEnum:
            KEY_A : Constant(desc="Hello", signed=True) = -1
    assert "Enumeration BadEnum contains negative value -1 (KEY_A)" in str(excinfo.value)

def test_enum_idx_duplicate():
    """ Check that an indexed enumeration detects duplicate values """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum()
        class DupEnum:
            KEY_A : Constant(desc="Description A") = 1
            KEY_B : Constant(desc="Description B") = 1
    assert "Value 1 (KEY_B) appears twice in DupEnum" in str(excinfo.value)

def test_enum_idx_oor():
    """ Check that an indexed enumeration detects out-of-range values """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum(width=2)
        class OOREnum:
            KEY_A : Constant(desc="Description A")
            KEY_B : Constant(desc="Description B")
            KEY_C : Constant(desc="Description C")
            KEY_D : Constant(desc="Description D")
            KEY_E : Constant(desc="Description E")
    assert "Value 4 (KEY_E) of OOREnum cannot be encoded within 2 bits" in str(excinfo.value)

def test_enum_1h_explicit():
    """ Check behaviour of an explicitly valued one-hot enumeration """
    @packtype.enum(mode="ONEHOT")
    class DummyEnum:
        """ Test description 12345 """
        KEY_A : Constant(desc="Description A") = 1
        KEY_B : Constant(desc="Description B") = 2
        KEY_C : Constant(desc="Description C") = 4
    assert DummyEnum._pt_desc == "Test description 12345"
    assert DummyEnum._pt_mode == "ONEHOT"
    assert DummyEnum.KEY_A.name == "KEY_A"
    assert DummyEnum.KEY_B.name == "KEY_B"
    assert DummyEnum.KEY_C.name == "KEY_C"
    assert DummyEnum.KEY_A.desc == "Description A"
    assert DummyEnum.KEY_B.desc == "Description B"
    assert DummyEnum.KEY_C.desc == "Description C"
    assert DummyEnum.KEY_A.value == 1
    assert DummyEnum.KEY_B.value == 2
    assert DummyEnum.KEY_C.value == 4
    assert DummyEnum._pt_width == 3

def test_enum_1h_auto():
    """ Check behaviour of an auto-valued one-hot enumeration """
    @packtype.enum(mode="ONEHOT")
    class DummyEnum:
        """ Test description 12345 """
        KEY_A : Constant(desc="Description A") # 1
        KEY_B : Constant(desc="Description B") # 2
        KEY_C : Constant(desc="Description C") # 4
        KEY_D : Constant(desc="Description D") = 32
        KEY_E : Constant(desc="Description E") # 64
    assert DummyEnum._pt_desc == "Test description 12345"
    assert DummyEnum._pt_mode == "ONEHOT"
    assert DummyEnum.KEY_A.name == "KEY_A"
    assert DummyEnum.KEY_B.name == "KEY_B"
    assert DummyEnum.KEY_C.name == "KEY_C"
    assert DummyEnum.KEY_D.name == "KEY_D"
    assert DummyEnum.KEY_E.name == "KEY_E"
    assert DummyEnum.KEY_A.desc == "Description A"
    assert DummyEnum.KEY_B.desc == "Description B"
    assert DummyEnum.KEY_C.desc == "Description C"
    assert DummyEnum.KEY_D.desc == "Description D"
    assert DummyEnum.KEY_E.desc == "Description E"
    assert DummyEnum.KEY_A.value == 1
    assert DummyEnum.KEY_B.value == 2
    assert DummyEnum.KEY_C.value == 4
    assert DummyEnum.KEY_D.value == 32
    assert DummyEnum.KEY_E.value == 64
    assert DummyEnum._pt_width == 7

def test_enum_1h_bad_value():
    """ Check that a one-hot enumeration detects non-one-hot values """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum(mode="ONEHOT")
        class BadEnum:
            KEY_A : Constant(desc="Hello") = 3
    assert "Value 3 (KEY_A) of BadEnum is not one-hot" in str(excinfo.value)

def test_enum_1h_oor():
    """ Check that a one-hot enumeration detects out-of-range values """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum(width=2, mode="ONEHOT")
        class OOREnum:
            KEY_A : Constant(desc="Description A")
            KEY_B : Constant(desc="Description B")
            KEY_C : Constant(desc="Description C")
    assert "Value 4 (KEY_C) of OOREnum cannot be encoded within 2 bits" in str(excinfo.value)

def test_enum_gray_explicit():
    """ Check behaviour of an explicitly valued gray coding """
    @packtype.enum(mode="GRAY")
    class DummyEnum:
        """ Test description 12345 """
        KEY_A : Constant(desc="Description A") = 0
        KEY_B : Constant(desc="Description B") = 1
        KEY_C : Constant(desc="Description C") = 3
    assert DummyEnum._pt_desc == "Test description 12345"
    assert DummyEnum._pt_mode == "GRAY"
    assert DummyEnum.KEY_A.name == "KEY_A"
    assert DummyEnum.KEY_B.name == "KEY_B"
    assert DummyEnum.KEY_C.name == "KEY_C"
    assert DummyEnum.KEY_A.desc == "Description A"
    assert DummyEnum.KEY_B.desc == "Description B"
    assert DummyEnum.KEY_C.desc == "Description C"
    assert DummyEnum.KEY_A.value == 0
    assert DummyEnum.KEY_B.value == 1
    assert DummyEnum.KEY_C.value == 3
    assert DummyEnum._pt_width == 2

def test_enum_gray_auto():
    """ Check behaviour of an auto-valued one-hot enumeration """
    @packtype.enum(mode="GRAY")
    class DummyEnum:
        """ Test description 12345 """
        KEY_A : Constant(desc="Description A")
        KEY_B : Constant(desc="Description B")
        KEY_C : Constant(desc="Description C")
        KEY_D : Constant(desc="Description D")
        KEY_E : Constant(desc="Description E")
    assert DummyEnum._pt_desc == "Test description 12345"
    assert DummyEnum._pt_mode == "GRAY"
    assert DummyEnum.KEY_A.name == "KEY_A"
    assert DummyEnum.KEY_B.name == "KEY_B"
    assert DummyEnum.KEY_C.name == "KEY_C"
    assert DummyEnum.KEY_D.name == "KEY_D"
    assert DummyEnum.KEY_E.name == "KEY_E"
    assert DummyEnum.KEY_A.desc == "Description A"
    assert DummyEnum.KEY_B.desc == "Description B"
    assert DummyEnum.KEY_C.desc == "Description C"
    assert DummyEnum.KEY_D.desc == "Description D"
    assert DummyEnum.KEY_E.desc == "Description E"
    assert DummyEnum.KEY_A.value == 0b000
    assert DummyEnum.KEY_B.value == 0b001
    assert DummyEnum.KEY_C.value == 0b011
    assert DummyEnum.KEY_D.value == 0b010
    assert DummyEnum.KEY_E.value == 0b110
    assert DummyEnum._pt_width == 3

def test_enum_gray_bad_value():
    """ Check that a one-hot enumeration detects non-one-hot values """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum(mode="GRAY")
        class BadEnum:
            KEY_A : Constant(desc="Hello") = 1
    assert "Value 1 (KEY_A) at index 0 of BadEnum is not gray-coded" in str(excinfo.value)

def test_enum_gray_oor():
    """ Check that a one-hot enumeration detects out-of-range values """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum(width=2, mode="GRAY")
        class OOREnum:
            KEY_A : Constant(desc="Description A") # 0
            KEY_B : Constant(desc="Description B") # 1
            KEY_C : Constant(desc="Description C") # 3
            KEY_D : Constant(desc="Description D") # 2
            KEY_E : Constant(desc="Description E") # 6
    assert "Value 6 (KEY_E) of OOREnum cannot be encoded within 2 bits" in str(excinfo.value)

def test_enum_iterate():
    """ Test difference types of iteration through an enumeration """
    @packtype.enum()
    class DummyEnum:
        KEY_A : Constant(desc="Description A") = 0
        KEY_B : Constant(desc="Description B") = 1
        KEY_C : Constant(desc="Description C") = 2
    # Check iteration of keys
    assert [x for x in DummyEnum._pt_keys()] == ["KEY_A", "KEY_B", "KEY_C"]
    # Check iteration of values
    assert [x for x in DummyEnum._pt_values()] == [
        DummyEnum.KEY_A, DummyEnum.KEY_B, DummyEnum.KEY_C
    ]
    # Check iteration of items (key/value pairs)
    assert [x for x in DummyEnum._pt_items()] == [
        ("KEY_A", DummyEnum.KEY_A),
        ("KEY_B", DummyEnum.KEY_B),
        ("KEY_C", DummyEnum.KEY_C)
    ]

def test_enum_raw_values():
    """ Test enum with raw integers """
    @packtype.enum()
    class DummyEnum:
        KEY_A = 1
        KEY_B = 2
        KEY_C = 3
    assert DummyEnum._pt_width == 2
    assert DummyEnum.KEY_A.value == 1
    assert DummyEnum.KEY_B.value == 2
    assert DummyEnum.KEY_C.value == 3

def test_enum_bad_values(capsys):
    """ Test enum with raw integers """
    @packtype.enum()
    class BadValueEnum:
        KEY_A = 1
        KEY_B = "hello"
        KEY_C = []
    assert capsys.readouterr().out == (
        "BadValueEnum ignoring field KEY_B of unknown type\n"
        "BadValueEnum ignoring field KEY_C of unknown type\n"
    )

def test_enum_no_legal_values():
    """ Test enum with raw integers """
    with pytest.raises(AssertionError) as excinfo:
        @packtype.enum()
        class NoLegalEnum:
            KEY_A = "hello"
            KEY_B = []
    assert "No legal fields found for NoLegalEnum" in str(excinfo.value)
