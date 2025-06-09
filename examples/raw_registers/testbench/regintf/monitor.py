# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from cocotb.triggers import RisingEdge
from forastero import BaseMonitor

from .transaction import RegResponse


class RegMonitor(BaseMonitor):
    async def monitor(self, capture):
        while True:
            write = self.io.get("write")
            if not self.io.get("enable"):
                await RisingEdge(self.clk)
                continue
            await RisingEdge(self.clk)
            capture(RegResponse(rd_data=0 if write else self.io.get("rd_data"),
                                error=self.io.get("error") != 0))
