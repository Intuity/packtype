# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

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
