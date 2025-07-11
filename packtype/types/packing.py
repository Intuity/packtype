# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from enum import Enum, auto


class Packing(Enum):
    FROM_LSB = auto()
    FROM_MSB = auto()
