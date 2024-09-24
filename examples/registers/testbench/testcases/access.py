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
from forastero import DriverEvent, MonitorEvent

from registers import Control, Version, Status

from ..regintf import RegRequest, RegResponse
from ..testbench import Testbench


@Testbench.testcase()
async def access_device(tb, log):
    """Read back from the identity, version, and status registers"""
    ctrl = Control()
    # Read the identity register
    log.info("Reading back identity")
    tb.drv.enqueue(RegRequest(address=ctrl.device.identity._pt_offset,
                              write=False))
    tb.scoreboard.channels["mon"].push_reference(RegResponse(
        rd_data=int(ctrl.device.identity),
    ))
    # Read the version register
    log.info("Reading back version (build randomised 100 times)")
    for _ in range(100):
        version = Version()
        version.build = tb.random.getrandbits(ctrl.device.version.build._pt_width)
        tb.internal.version.value = int(version)
        tb.internal.version_strobe.value = 1
        await RisingEdge(tb.clk)
        tb.internal.version_strobe.value = 0
        tb.drv.enqueue(RegRequest(
            address=ctrl.device.version._pt_offset,
            write=False
        ))
        tb.scoreboard.channels["mon"].push_reference(RegResponse(
            rd_data=int(version),
        ))
        await tb.mon.wait_for(MonitorEvent.CAPTURE)
    # Read back the status register
    log.info("Reading back status (randomised 100 times)")
    for _ in range(100):
        sts = Status._pt_unpack(tb.random.getrandbits(Status._PT_WIDTH))
        tb.internal.status.value = int(sts)
        tb.internal.status_strobe.value = 1
        await RisingEdge(tb.clk)
        tb.internal.status_strobe.value = 0
        tb.drv.enqueue(RegRequest(
            address=ctrl.device.status._pt_offset,
            write=False,
        ))
        tb.scoreboard.channels["mon"].push_reference(RegResponse(
            rd_data=int(sts),
        ))
        await tb.mon.wait_for(MonitorEvent.CAPTURE)


@Testbench.testcase()
async def access_control(tb, log):
    """Write to the reset control registers"""
    ctrl = Control()
    resets = ctrl.control.core_reset
    for idx in range(100):
        # Decide on a state to write
        state = [tb.random.getrandbits(resets[0]._pt_width) for _ in resets]
        log.info(f"Pass {idx} setting resets to {state}")
        # Write the state
        for value, reset in zip(state, resets):
            event = tb.drv.enqueue(RegRequest(
                address=reset._pt_offset,
                write=True,
                wr_data=value,
            ), wait_for=DriverEvent.POST_DRIVE)
            tb.scoreboard.channels["mon"].push_reference(RegResponse())
        # Wait for the final value to be sunk
        log.info("Waiting for writes to be sunk")
        await event.wait()
        await RisingEdge(tb.clk)
        # Check state
        log.info("Checking state")
        for idx, value in enumerate(state):
            got = int(tb.internal.core_reset[idx].value)
            assert got == value, f"Reset {idx} - expected: {value} got: {got}"
