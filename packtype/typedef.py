# Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk
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

from typing import Iterable

from .base import Base
from .container import Container
from .constant import Constant

class Typedef(Container):
    """ A simple named fixed-width data structure """

    def __init__(self, width=None, alias=None, name=None, desc=None):
        """ Initialise structure with name and fields

        Args:
            width: Bit width
            alias: Alias another type
            name : Optional name of the container
            desc : Optional description
        """
        super().__init__(name=name, width=width)
        # Sanity check width
        assert (width is None) or (isinstance(width, (int, Constant)) or width >= 0), \
            f"Width must be None or a positive integer, not '{width}'"
        # Sanith check alias
        assert (alias is None) or (isinstance(alias, Container)), \
            f"Alias must be None or a container reference, not '{alias}'"
        # Sanity check only one of width or alias provided
        assert (width is None) or (alias is None), \
            "Only one of width or alias can be defined"
        # Record alias
        self.__alias = alias

    @property
    def _pt_alias(self):
        return self.__alias

    @property
    def _pt_width(self):
        return self.__alias._pt_width if self.__alias else super()._pt_width

    @_pt_width.setter
    def _pt_width(self, width):
        assert self.__alias is None, \
            f"Trying to set width on alias typedef {self.__name}"
        super()._pt_width = width

    def _pt_foreign(self,
                    exclude: list["Container"] | None = None) -> Iterable["Container"]:
        """
        Identify all foreign types referenced by this container and any of its
        children, excluding types that inherit from a provided list of parents.

        :param exclude: Parent objects to exclude
        :returns: The set of foreign types
        """
        exclude = exclude or [self]
        if self in exclude or self._pt_parent in exclude:
            if isinstance(self.__alias, Base):
                yield from self.__alias._pt_foreign(exclude)
        else:
            yield self
