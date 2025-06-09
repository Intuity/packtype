# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import dataclasses

from forastero import BaseTransaction


@dataclasses.dataclass(kw_only=True)
class RegRequest(BaseTransaction):
    address: int = 0
    write: bool = False
    wr_data: int = 0


@dataclasses.dataclass(kw_only=True)
class RegResponse(BaseTransaction):
    rd_data: int = 0
    error: bool = False
