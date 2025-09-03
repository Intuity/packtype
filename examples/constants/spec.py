# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Constant, Scalar


@packtype.package()
class DateConsts:
    """Constants to do with date and time"""

    DAYS_PER_YEAR: Constant = 365
    DAYS_PER_WEEK: Constant = 7
    HOURS_PER_DAY: Constant[8] = 24
    MINS_PER_HOUR: Constant = 60


@DateConsts.enum()
class Weekday:
    MON: Constant
    TUE: Constant
    WED: Constant
    THU: Constant
    FRI: Constant
    SAT: Constant
    SUN: Constant


@DateConsts.enum()
class Month:
    JAN: Constant
    FEB: Constant
    MAR: Constant
    APR: Constant
    MAY: Constant
    JUN: Constant
    JUL: Constant
    AUG: Constant
    SEP: Constant
    OCT: Constant
    NOV: Constant
    DEC: Constant


@DateConsts.struct()
class Date:
    year: Scalar[12]
    month: Month
    day: Scalar[5]


DateConsts._pt_attach_instance("START_OF_WEEK", Weekday.MON)
DateConsts._pt_attach_instance("END_OF_WEEK", Weekday.SUN)
DateConsts._pt_attach_instance("CHRISTMAS", Date(year=2025, month=Month.DEC, day=25))
