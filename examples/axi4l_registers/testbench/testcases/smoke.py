# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from cocotb.triggers import ClockCycles

from ..testbench import Testbench


@Testbench.testcase()
async def smoke(tb, log):
    log.info("Waiting for 100 cycles")
    await ClockCycles(tb.clk, 100)
    log.info("Timer elapsed")
