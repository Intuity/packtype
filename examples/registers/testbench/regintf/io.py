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

from forastero import BaseIO


class RegIntfIO(BaseIO):

    def __init__(self, dut, name, role, io_style=None):
        super().__init__(
            dut,
            name,
            role,
            init_sigs=["address", "wr_data", "write", "enable"],
            resp_sigs=["rd_data", "error"],
            io_style=io_style,
        )
