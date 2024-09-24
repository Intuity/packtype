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
from forastero import MonitorEvent

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
