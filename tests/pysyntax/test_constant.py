# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math

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
    assert TestPkg.A**TestPkg.B == (35**17)
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
    assert TestPkg.A**17 == (35**17)
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
    assert 35**TestPkg.B == (35**17)
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
    assert val == (35**17)
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

    # Check that math functions work without casting
    math.log2(TestPkg.A) == math.log2(35)

    # For that the value can be used as an index
    expected = 0
    for idx in range(TestPkg.A):
        assert idx == expected
        expected += 1


def test_constant_reference():
    @packtype.package()
    class PkgA:
        A: Constant = 123

    @packtype.package()
    class PkgB:
        B: Constant = PkgA.A

    assert isinstance(PkgB.B.value, int)
    assert PkgB.B.value == 123
    assert int(PkgB.B) == 123
