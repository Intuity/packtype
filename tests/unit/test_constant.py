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
from packtype import Constant

from ..fixtures import reset_registry

assert reset_registry

def test_constant_arithmetic():
    @packtype.package()
    class TestPkg:
        A: Constant = 35
        B: Constant = 17

    # Constant-Constant operations
    assert TestPkg.A + TestPkg.B == (35 + 17)
    assert TestPkg.A - TestPkg.B == (35 - 17)
    assert TestPkg.A * TestPkg.B == (35 * 17)
    assert TestPkg.A / TestPkg.B == (35 / 17)
    assert TestPkg.A // TestPkg.B == (35 // 17)
    assert TestPkg.A % TestPkg.B == (35 % 17)
    assert divmod(TestPkg.A, TestPkg.B) == divmod(35, 17)
    assert TestPkg.A ** TestPkg.B == (35 ** 17)
    assert TestPkg.A << TestPkg.B == (35 << 17)
    assert TestPkg.A >> TestPkg.B == (35 >> 17)
    assert TestPkg.A & TestPkg.B == (35 & 17)
    assert TestPkg.A ^ TestPkg.B == (35 ^ 17)
    assert TestPkg.A | TestPkg.B == (35 | 17)

    # Constant-int operations
    assert TestPkg.A + 17 == (35 + 17)
    assert TestPkg.A - 17 == (35 - 17)
    assert TestPkg.A * 17 == (35 * 17)
    assert TestPkg.A / 17 == (35 / 17)
    assert TestPkg.A // 17 == (35 // 17)
    assert TestPkg.A % 17 == (35 % 17)
    assert divmod(TestPkg.A, 17) == divmod(35, 17)
    assert TestPkg.A ** 17 == (35 ** 17)
    assert TestPkg.A << 17 == (35 << 17)
    assert TestPkg.A >> 17 == (35 >> 17)
    assert TestPkg.A & 17 == (35 & 17)
    assert TestPkg.A ^ 17 == (35 ^ 17)
    assert TestPkg.A | 17 == (35 | 17)

    # int-Constant operations
    assert 35 + TestPkg.B == (35 + 17)
    assert 35 - TestPkg.B == (35 - 17)
    assert 35 * TestPkg.B == (35 * 17)
    assert 35 / TestPkg.B == (35 / 17)
    assert 35 // TestPkg.B == (35 // 17)
    assert 35 % TestPkg.B == (35 % 17)
    assert divmod(35, TestPkg.B) == divmod(35, 17)
    assert 35 ** TestPkg.B == (35 ** 17)
    assert 35 << TestPkg.B == (35 << 17)
    assert 35 >> TestPkg.B == (35 >> 17)
    assert 35 & TestPkg.B == (35 & 17)
    assert 35 ^ TestPkg.B == (35 ^ 17)
    assert 35 | TestPkg.B == (35 | 17)

    # In-place constant operations
    val = TestPkg.A
    val += TestPkg.B
    assert val == (35 + 17)
    val = TestPkg.A
    val -= TestPkg.B
    assert val == (35 - 17)
    val = TestPkg.A
    val *= TestPkg.B
    assert val == (35 * 17)
    val = TestPkg.A
    val /= TestPkg.B
    assert val == (35 / 17)
    val = TestPkg.A
    val //= TestPkg.B
    assert val == (35 // 17)
    val = TestPkg.A
    val %= TestPkg.B
    assert val == (35 % 17)
    val = TestPkg.A
    val **= TestPkg.B
    assert val == (35 ** 17)
    val = TestPkg.A
    val <<= TestPkg.B
    assert val == (35 << 17)
    val = TestPkg.A
    val >>= TestPkg.B
    assert val == (35 >> 17)
    val = TestPkg.A
    val &= TestPkg.B
    assert val == (35 & 17)
    val = TestPkg.A
    val ^= TestPkg.B
    assert val == (35 ^ 17)
    val = TestPkg.A
    val |= TestPkg.B
    assert val == (35 | 17)

    # Unary operations
    assert -TestPkg.A == -35
    assert +TestPkg.A == 35
    assert abs(TestPkg.A) == 35
    assert ~TestPkg.A == ~35

    # Comparisons
    assert (TestPkg.A < TestPkg.B) == (35 < 17)
    assert (TestPkg.A <= TestPkg.B) == (35 <= 17)
    assert (TestPkg.A == TestPkg.B) == (35 == 17)
    assert (TestPkg.A != TestPkg.B) == (35 != 17)
    assert (TestPkg.A > TestPkg.B) == (35 > 17)
    assert (TestPkg.A >= TestPkg.B) == (35 >= 17)
