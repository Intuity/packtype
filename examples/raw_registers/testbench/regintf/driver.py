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

from cocotb.triggers import RisingEdge
from forastero import BaseDriver

from .transaction import RegRequest


class RegDriver(BaseDriver):
    async def drive(self, obj: RegRequest):
        self.io.set("address", obj.address)
        self.io.set("wr_data", obj.wr_data)
        self.io.set("write", obj.write)
        self.io.set("enable", True)
        await RisingEdge(self.clk)
        self.io.set("enable", False)
