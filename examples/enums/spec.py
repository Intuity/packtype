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

import packtype
from packtype import Constant
from packtype.enum import Enum


@packtype.package()
class Types:
    pass


@packtype.enum(package=Types, mode=Enum.INDEXED)
class IndexedExplicit:
    VALUE_A: Constant("First value") = 0
    VALUE_B: Constant("Second value") = 1
    VALUE_C: Constant("Third value") = 2
    VALUE_D: Constant("Fourth value") = 3


@packtype.enum(package=Types, mode=Enum.INDEXED)
class IndexedAutomatic:
    VALUE_A: Constant("First value")
    VALUE_B: Constant("Second value")
    VALUE_C: Constant("Third value")
    VALUE_D: Constant("Fourth value")


@packtype.enum(package=Types, mode=Enum.ONEHOT)
class OneHot:
    VALUE_A: Constant("First value")
    VALUE_B: Constant("Second value")
    VALUE_C: Constant("Third value")
    VALUE_D: Constant("Fourth value")


@packtype.enum(package=Types, mode=Enum.GRAY)
class GrayCode:
    VALUE_A: Constant("First value")
    VALUE_B: Constant("Second value")
    VALUE_C: Constant("Third value")
    VALUE_D: Constant("Fourth value")
