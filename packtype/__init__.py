# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from .alias import Alias
from .assembly import Packing
from .constant import Constant
from .enum import EnumMode
from .package import Package
from .scalar import Scalar
from .wrap import get_wrapper

package = get_wrapper(Package)

# Guards
assert all((Alias, Constant, EnumMode, Package, Packing, Scalar, package))
