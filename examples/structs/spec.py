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
from packtype import Scalar, Struct

@packtype.package()
class Calendar:
    pass

@packtype.struct(package=Calendar)
class Date:
    day   : Scalar(width= 5, desc="Day of month 1-31" )
    month : Scalar(width= 4, desc="Month of year 1-12")
    year  : Scalar(width=12, desc="Year e.g. 2021"    )

@packtype.struct(package=Calendar, pack=Struct.FROM_MSB, width=17)
class Time:
    hour   : Scalar(width=5, desc="Hour of day 0-23"     )
    minute : Scalar(width=6, desc="Minute of hour 0-59"  )
    second : Scalar(width=6, desc="Second of minute 0-59")

@packtype.struct(package=Calendar)
class DateTime:
    date : Date(desc="Full date"        )
    time : Time(desc="Full 24 hour time")
