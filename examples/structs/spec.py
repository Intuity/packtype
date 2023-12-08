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
from packtype import Packing, Scalar


@packtype.package()
class Calendar:
    pass


@Calendar.struct()
class Date:
    day: Scalar[5]
    month: Scalar[4]
    year: Scalar[12]


@Calendar.struct(packing=Packing.FROM_MSB, width=17)
class Time:
    hour: Scalar[5]
    minute: Scalar[6]
    second: Scalar[6]


@Calendar.struct()
class DateTime:
    date: Date
    time: Time
