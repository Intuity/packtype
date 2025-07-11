# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.types.wrap import Registry


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the contents of the registry before every test"""
    Registry.reset()
    yield
