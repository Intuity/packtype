# Copyright 2024, Peter Birch, mailto:peter@intuity.io
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


@packtype.package()
class DateConsts:
    """Constants to do with date and time"""

    DAYS_PER_YEAR: Constant = 365
    DAYS_PER_WEEK: Constant = 7
    HOURS_PER_DAY: Constant = 24
    MINS_PER_HOUR: Constant = 60
