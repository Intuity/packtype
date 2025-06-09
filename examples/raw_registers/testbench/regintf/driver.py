# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

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
