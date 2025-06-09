# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from cocotb.triggers import ClockCycles, RisingEdge
from forastero import MonitorEvent
from forastero_io.axi4lite.sequences import axi4lite_b_backpressure, axi4lite_r_backpressure
from forastero_io.axi4lite.transaction import AXI4LiteReadAddress, AXI4LiteReadResponse, AXI4LiteWriteAddress, AXI4LiteWriteData, AXI4LiteWriteResponse
from packtype.registers import Behaviour

from registers import Control, Version, Status

from ..testbench import Testbench


@Testbench.testcase()
async def access_device(tb, log):
    """Read back from the identity, version, and status registers"""
    # Randomise backpressure
    tb.schedule(axi4lite_b_backpressure(driver=tb.b_drv), blocking=False)
    tb.schedule(axi4lite_r_backpressure(driver=tb.r_drv), blocking=False)
    # Create register bank instance
    ctrl = Control()
    # Read the identity register
    log.info("Reading back identity")
    tb.ar_drv.enqueue(AXI4LiteReadAddress(address=ctrl.device.identity._pt_offset))
    tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(
        data=int(ctrl.device.identity),
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
        tb.ar_drv.enqueue(AXI4LiteReadAddress(address=ctrl.device.version._pt_offset))
        tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(
            data=int(version),
        ))
        await tb.r_mon.wait_for(MonitorEvent.CAPTURE)
    # Read back the status register
    log.info("Reading back status (randomised 100 times)")
    for _ in range(100):
        sts = Status._pt_unpack(tb.random.getrandbits(Status._PT_WIDTH))
        tb.internal.status.value = int(sts)
        tb.internal.status_strobe.value = 1
        await RisingEdge(tb.clk)
        tb.internal.status_strobe.value = 0
        tb.ar_drv.enqueue(AXI4LiteReadAddress(address=ctrl.device.status._pt_offset))
        tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(data=int(sts)))
        await tb.r_mon.wait_for(MonitorEvent.CAPTURE)


@Testbench.testcase()
async def access_control(tb, log):
    """Write to the reset control registers"""
    # Randomise backpressure
    tb.schedule(axi4lite_b_backpressure(driver=tb.b_drv), blocking=False)
    tb.schedule(axi4lite_r_backpressure(driver=tb.r_drv), blocking=False)
    # Create register bank instance
    ctrl = Control()
    # Randomise accesses to core reset signals
    resets = ctrl.control.core_reset
    for idx in range(100):
        # Decide on a state to write
        state = [tb.random.getrandbits(resets[0]._pt_width) for _ in resets]
        log.info(f"Pass {idx} setting resets to {state}")
        # Write the state
        for value, reset in zip(state, resets):
            tb.aw_drv.enqueue(AXI4LiteWriteAddress(address=reset._pt_offset))
            tb.w_drv.enqueue(AXI4LiteWriteData(data=value, strobe=0xFF))
            tb.scoreboard.channels["b_mon"].push_reference(AXI4LiteWriteResponse())
        # Wait for the write responses
        log.info("Waiting for writes to be sunk")
        for _ in resets:
            await tb.b_mon.wait_for(MonitorEvent.CAPTURE)
        # Check state
        log.info("Checking state")
        for idx, value in enumerate(state):
            got = int(tb.internal.core_reset[idx].value)
            assert got == value, f"Reset {idx} - expected: {value} got: {got}"


@Testbench.testcase()
async def access_fifo_h2d(tb, log):
    """Exercise H2D FIFOs"""
    # Randomise backpressure
    tb.schedule(axi4lite_b_backpressure(driver=tb.b_drv), blocking=False)
    tb.schedule(axi4lite_r_backpressure(driver=tb.r_drv), blocking=False)
    # Create register bank instance
    ctrl = Control()
    # Randomise H2D FIFO access
    for idx in range(100):
        comm_idx = tb.random.randint(0, len(ctrl.comms)-1)
        comm = ctrl.comms[comm_idx]
        log.info(f"Pass {idx} exercising channel {comm_idx}")
        # Push a bunch of entries into the X2I FIFO
        values = []
        for _ in range(tb.random.randint(1, comm.h2d._PT_DEPTH)):
            values.append(value := tb.random.getrandbits(comm.h2d._pt_width))
            tb.aw_drv.enqueue(AXI4LiteWriteAddress(address=comm.h2d._pt_offset))
            tb.w_drv.enqueue(AXI4LiteWriteData(data=value))
            tb.scoreboard.channels["b_mon"].push_reference(AXI4LiteWriteResponse())
        for _ in values:
            await tb.b_mon.wait_for(MonitorEvent.CAPTURE)
        # Read back the level
        tb.ar_drv.enqueue(AXI4LiteReadAddress(
            address=comm.h2d._pt_paired[Behaviour.LEVEL]._pt_offset,
        ))
        await tb.r_mon.wait_for(MonitorEvent.CAPTURE)
        tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(data=len(values)))
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
        tb.ar_drv.enqueue(AXI4LiteReadAddress(
            address=comm.h2d._pt_paired[Behaviour.LEVEL]._pt_offset,
        ))
        await tb.r_mon.wait_for(MonitorEvent.CAPTURE)
        tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(data=0))
        # Check the internally visible level
        assert int(tb.internal.comms_h2d_level[comm_idx].value) == 0


@Testbench.testcase()
async def access_fifo_d2h(tb, log):
    """Exercise D2H FIFOs"""
    # Randomise backpressure
    tb.schedule(axi4lite_b_backpressure(driver=tb.b_drv), blocking=False)
    tb.schedule(axi4lite_r_backpressure(driver=tb.r_drv), blocking=False)
    # Create register bank instance
    ctrl = Control()
    # Randomise D2H FIFO access
    for idx in range(100):
        comm_idx = tb.random.randint(0, len(ctrl.comms)-1)
        comm = ctrl.comms[comm_idx]
        log.info(f"Pass {idx} exercising channel {comm_idx}")
        # Push a bunch of entries into the I2X FIFO
        values = []
        for _ in range(tb.random.randint(1, comm.d2h._PT_DEPTH)):
            values.append(value := tb.random.getrandbits(comm.d2h._pt_width))
            tb.internal.comms_d2h[comm_idx].value = value
            tb.internal.comms_d2h_valid[comm_idx].value = 1
            await RisingEdge(tb.clk)
            tb.internal.comms_d2h_valid[comm_idx].value = 0
            await ClockCycles(tb.clk, tb.random.randint(0, 10))
        # Read back the level
        tb.ar_drv.enqueue(AXI4LiteReadAddress(
            address=comm.d2h._pt_paired[Behaviour.LEVEL]._pt_offset,
        ))
        tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(data=len(values)))
        log.info("Waiting for read of level")
        await tb.r_mon.wait_for(MonitorEvent.CAPTURE)
        # Check the internally visible level
        assert int(tb.internal.comms_d2h_level[comm_idx].value) == len(values)
        # Pop externally
        for idx, value in enumerate(values):
            # Read back to pop the value
            tb.ar_drv.enqueue(AXI4LiteReadAddress(address=comm.d2h._pt_offset))
            tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(data=value))
        log.info(f"Waiting for read back of {len(values)} values")
        for _ in values:
            await tb.r_mon.wait_for(MonitorEvent.CAPTURE)
        # Read back the level again (should get a zero)
        tb.ar_drv.enqueue(AXI4LiteReadAddress(
            address=comm.d2h._pt_paired[Behaviour.LEVEL]._pt_offset,
        ))
        tb.scoreboard.channels["r_mon"].push_reference(AXI4LiteReadResponse(data=0))
        log.info("Waiting for read of empty level")
        await tb.r_mon.wait_for(MonitorEvent.CAPTURE)
        # Check the internally visible level
        assert int(tb.internal.comms_d2h_level[comm_idx].value) == 0
