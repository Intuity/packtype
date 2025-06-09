# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from types import SimpleNamespace

from forastero import BaseBench, IORole

from .regintf import RegDriver, RegIntfIO, RegMonitor


class Testbench(BaseBench):
    """Testbench for the raw register interface"""

    def __init__(self, dut):
        super().__init__(dut, clk=dut.i_clk, rst=dut.i_rst)
        # Register interface
        reg_io = RegIntfIO(dut, None, IORole.RESPONDER)
        self.register("drv", RegDriver(self, reg_io, self.clk, self.rst))
        self.register("mon", RegMonitor(self, reg_io, self.clk, self.rst))
        # Internal I/O
        self.internal = SimpleNamespace(
            version=self.dut.i_device_version_data,
            version_strobe=self.dut.i_device_version_strobe,
            status=self.dut.i_device_status_data,
            status_strobe=self.dut.i_device_status_strobe,
            core_reset=(self.dut.o_control_core_reset_0_data,
                        self.dut.o_control_core_reset_1_data,
                        self.dut.o_control_core_reset_2_data,
                        self.dut.o_control_core_reset_3_data),
            core_reset_strobe=(self.dut.o_control_core_reset_0_strobe,
                               self.dut.o_control_core_reset_1_strobe,
                               self.dut.o_control_core_reset_2_strobe,
                               self.dut.o_control_core_reset_3_strobe),
            comms_h2d=(self.dut.o_comms_0_h2d_data,
                       self.dut.o_comms_1_h2d_data),
            comms_h2d_valid=(self.dut.o_comms_0_h2d_valid,
                             self.dut.o_comms_1_h2d_valid),
            comms_h2d_ready=(self.dut.i_comms_0_h2d_ready,
                             self.dut.i_comms_1_h2d_ready),
            comms_h2d_level=(self.dut.o_comms_0_h2d_level,
                             self.dut.o_comms_1_h2d_level),
            comms_d2h=(self.dut.i_comms_0_d2h_data,
                       self.dut.i_comms_1_d2h_data),
            comms_d2h_valid=(self.dut.i_comms_0_d2h_valid,
                             self.dut.i_comms_1_d2h_valid),
            comms_d2h_ready=(self.dut.o_comms_0_d2h_ready,
                             self.dut.o_comms_1_d2h_ready),
            comms_d2h_level=(self.dut.o_comms_0_d2h_level,
                             self.dut.o_comms_1_d2h_level),
        )

    async def initialise(self) -> None:
        super().initialise()
        self.internal.version.value = 0
        self.internal.version_strobe.value = 0
        self.internal.status.value = 0
        self.internal.status_strobe.value = 0
        for idx in range(2):
            self.internal.comms_h2d_ready[idx].value = 0
        for idx in range(2):
            self.internal.comms_d2h[idx].value = 0
            self.internal.comms_d2h_valid[idx].value = 0
