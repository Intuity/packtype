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

from cocotb.triggers import ClockCycles, RisingEdge
from forastero import DriverEvent, MonitorEvent
from packtype.registers import Behaviour

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


@Testbench.testcase()
async def access_fifos(tb, log):
    """Exercise FIFOs"""
    ctrl = Control()
    for idx in range(100):
        comm_idx = tb.random.randint(0, len(ctrl.comms)-1)
        comm = ctrl.comms[comm_idx]
        log.info(f"Pass {idx} exercising channel {comm_idx}")
        # Push a bunch of entries into the X2I FIFO
        values = []
        for _ in range(tb.random.randint(1, comm.h2d._PT_DEPTH)):
            values.append(value := tb.random.getrandbits(comm.h2d._pt_width))
            event = tb.drv.enqueue(RegRequest(
                address=comm.h2d._pt_offset,
                write=True,
                wr_data=value,
            ), wait_for=DriverEvent.POST_DRIVE)
            tb.scoreboard.channels["mon"].push_reference(RegResponse())
        await event.wait()
        # Read back the level
        await tb.drv.enqueue(RegRequest(
            address=comm.h2d._pt_paired[Behaviour.LEVEL]._pt_offset,
            write=False,
        ), wait_for=DriverEvent.POST_DRIVE).wait()
        tb.scoreboard.channels["mon"].push_reference(RegResponse(rd_data=len(values)))
        # Check the internally visible level
        assert int(tb.internal.comms_h2d_level[comm_idx].value) == len(values)
        # Pop internally
        for idx, value in enumerate(values):
            # Drive ready to 'pop' the presented value
            tb.internal.comms_h2d_ready[comm_idx].value = 1
            await RisingEdge(tb.clk)
            tb.internal.comms_h2d_ready[comm_idx].value = 0
            # Check status
            log.info(f"Popping internal index {idx} -> 0x{value:016X}")
            got = int(tb.internal.comms_h2d[comm_idx].value)
            assert got == value, f"Index {idx} - got: 0x{got:016X}, expected: 0x{value:016X}"
            assert int(tb.internal.comms_h2d_valid[comm_idx].value) == 1
            # Wait a while
            await ClockCycles(tb.clk, tb.random.randint(0, 10))
        # Read back the level again (should get a zero)
        await tb.drv.enqueue(RegRequest(
            address=comm.h2d._pt_paired[Behaviour.LEVEL]._pt_offset,
            write=False,
        ), wait_for=DriverEvent.POST_DRIVE).wait()
        tb.scoreboard.channels["mon"].push_reference(RegResponse(rd_data=0))
        # Check the internally visible level
        assert int(tb.internal.comms_h2d_level[comm_idx].value) == 0
