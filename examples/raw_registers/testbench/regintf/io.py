# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

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
