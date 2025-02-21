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
