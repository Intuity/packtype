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
from .constant import Constant

class Container(Base):
    """ Base type for a fixed size, multi-field container """

    def __init__(self, name=None, fields=None, desc=None, width=None, legal=None, mutable=False, parent=None):
        """ Initialise container with a name and fields

        Args:
            name   : Name of the container
            fields : Dictionary of fields
            desc   : Optional description
            width  : Optional bit width (can be filled in later)
            legal  : Optional list of legal field types
            mutable: Can fields be appended after construction (default: False)
            parent : Pointer to parent (default: None)
        """
        super().__init__()
        # Setup properties
        assert name is None or isinstance(name, str), f"Name must be a string: {type(name)}"
        assert fields is None or isinstance(fields, dict), f"Fields must be a dict: {type(fields)}"
        assert width is None or (isinstance(width, (int, Constant)) and width > 0), \
            f"{type(self).__name__} {width} width must be a positive integer: {width}"
        assert legal is None or type(legal) in (list, tuple), \
            f"Legal field types must be a list or tuple if provided"
        assert isinstance(mutable, bool), f"Mutable must be boolean: {type(mutable)}"
        assert parent is None or isinstance(parent, Container), \
            f"Parent must be None or inheriting from Container: {type(parent)}"
        self.__name    = name
        self.__desc    = desc
        self.__fields  = fields or {}
        self.__width   = width
        self.__legal   = legal
        self.__mutable = mutable
        self.__parent  = parent
        # Check that all fields obey legal types
        for key, obj in self.__fields.items():
            assert self._pt_check(obj), \
                f"Field '{key}' of {self.__name} must be within: " \
                f"{', '.join([x.__name__ for x in self.__legal])}"

    def _pt_check(self, obj):
        """ Check if a particular object is allowed according to the legal list.

        Args:
            obj: The object to test
        """
        from .instance import Instance
        if self.__legal:
            if isinstance(obj, Instance):
                return any(x for x in self.__legal if isinstance(obj._pt_container, x))
            else:
                return any(x for x in self.__legal if isinstance(obj, x))
        else:
            return True

    def _pt_append(self, key, obj):
        """ Append a new field to the package

        Args:
            key: Name of the field
            obj: The object to add
        """
        assert self.__mutable, f"{self._pt_name} is not a mutable object"
        assert key not in self._pt_keys(), \
            f"Field '{key}' already present in {self._pt_name}"
        assert self._pt_check(obj), \
            f"Field '{key}' of {self._pt_name} must be within: " \
            f"{', '.join([x.__name__ for x in self.__legal])}"
        self.__fields[key] = obj

    def __call__(self, *args, **kwargs):
        from .instance import Instance
        return Instance(self, *args, **kwargs)

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if name in self.__fields:
                return self.__fields[name]
            else:
                raise e

    @property
    def _pt_name(self):
        return self.__name

    @_pt_name.setter
    def _pt_name(self, value):
        self.__name = value

    @property
    def _pt_fields(self):
        return { k: v for k, v in self.__fields.items() }
    @property
    def _pt_keys(self):
        return self.__fields.keys
    @property
    def _pt_values(self):
        return self.__fields.values
    @property
    def _pt_items(self):
        return self.__fields.items

    @property
    def _pt_desc(self):
        return self.__desc
    @_pt_desc.setter
    def _pt_desc(self, desc):
        assert not self.__desc, f"Trying to alter description of {self.__name}"
        assert isinstance(desc, str), f"Description must be a string: {desc}"
        self.__desc = desc

    @property
    def _pt_width(self):
        return self.__width
    @_pt_width.setter
    def _pt_width(self, width):
        assert self.__width is None, \
            f"Trying to override fixed width of {self.__name}"
        assert isinstance(width, (int, Constant)) and width > 0, \
            f"{type(self).__name__} {width} width must be a positive integer: {width}"
        self.__width = width

    @property
    def _pt_mask(self):
        return ((1 << self._pt_width) - 1)

    @property
    def _pt_parent(self):
        return self.__parent

    @_pt_parent.setter
    def _pt_parent(self, parent):
        assert self.__parent is None, "Attempting to overwrite parent"
        self.__parent = parent

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
            for field in self.__fields.values():
                if isinstance(field, Base):
                    yield from field._pt_foreign(exclude)
        else:
            yield self
