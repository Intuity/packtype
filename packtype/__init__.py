# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from .types.alias import Alias
from .types.assembly import Packing
from .types.constant import Constant
from .types.enum import EnumMode
from .types.package import Package
from .types.scalar import Scalar
from .types.wrap import get_wrapper

package = get_wrapper(Package)

# Guards
assert all((Alias, Constant, EnumMode, Package, Packing, Scalar, package))
