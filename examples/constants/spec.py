# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Constant


@packtype.package()
class DateConsts:
    """Constants to do with date and time"""

    DAYS_PER_YEAR: Constant = 365
    DAYS_PER_WEEK: Constant = 7
    HOURS_PER_DAY: Constant = 24
    MINS_PER_HOUR: Constant = 60
