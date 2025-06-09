# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Constant, EnumMode


@packtype.package()
class Types:
    pass


@Types.enum(mode=EnumMode.INDEXED)
class IndexedExplicit:
    VALUE_A: Constant = 0
    VALUE_B: Constant = 1
    VALUE_C: Constant = 2
    VALUE_D: Constant = 3


@Types.enum(mode=EnumMode.INDEXED)
class IndexedAutomatic:
    VALUE_A: Constant
    VALUE_B: Constant
    VALUE_C: Constant
    VALUE_D: Constant


@Types.enum(mode=EnumMode.ONE_HOT)
class OneHot:
    VALUE_A: Constant
    VALUE_B: Constant
    VALUE_C: Constant
    VALUE_D: Constant


@Types.enum(mode=EnumMode.GRAY)
class GrayCode:
    VALUE_A: Constant
    VALUE_B: Constant
    VALUE_C: Constant
    VALUE_D: Constant
