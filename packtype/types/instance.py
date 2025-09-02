# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from .base import Base


class Instance:

    def __init__(self, name: str, instance: Base):
        self.name = name
        self.instance = instance

    def __str__(self):
        return f"<Instance name={self.name} instance={self.instance}>"

    def __repr__(self):
        return str(self)
