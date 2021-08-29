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

from .base import Base

class Container(Base):
    """ Base type for a fixed size, multi-field container """

    def __init__(self, name, fields, width=None, legal=None):
        """ Initialise container with a name and fields

        Args:
            name  : Name of the container
            fields: Dictionary of fields
            width : Optional bit width (can be filled in later)
            legal : Optional list of legal field types
        """
        super().__init__()
        # Setup properties
        assert isinstance(name, str), f"Name must be a string: {type(name)}"
        assert isinstance(fields, dict), f"Fields must be a dict: {type(fields)}"
        assert width == None or (isinstance(width, int) and width > 0), \
            f"Enum {width} width must be a positive integer: {width}"
        assert legal == None or type(legal) in (list, tuple), \
            f"Legal field types must be a list or tuple if provided"
        self.__name   = name
        self.__fields = fields
        self.__width  = width
        self.__legal  = legal
        # Check that all fields obey legal types
        from .instance import Instance
        if self.__legal:
            for key, obj in self.__fields.items():
                if isinstance(obj, Instance):
                    assert any(x for x in self.__legal if isinstance(obj._pt_container, x)), \
                        f"Field '{key}' of {self.__name} must be within: {self.__legal}"
                else:
                    assert any(x for x in self.__legal if isinstance(obj, x)), \
                        f"Field '{key}' of {self.__name} must be within: {self.__legal}"

    def __call__(self, *args, **kwargs):
        from .instance import Instance
        return Instance(self, *args, **kwargs)

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return self.__fields[name]

    @property
    def _pt_name(self): return self.__name

    @property
    def _pt_fields(self): return { k: v for k, v in self.__fields.items() }
    @property
    def _pt_keys(self): return self.__fields.keys
    @property
    def _pt_values(self): return self.__fields.values
    @property
    def _pt_items(self): return self.__fields.items

    @property
    def _pt_width(self): return self.__width
    @_pt_width.setter
    def _pt_width(self, width):
        assert self.__width == None, \
            f"Trying to override fixed width of {self.__name}"
        assert isinstance(width, int) and width > 0, \
            f"Enum {width} width must be a positive integer: {width}"
        self.__width = width

    def _pt_assign(self, _value):
        raise Exception(f"{type(self).__name__} does not support assignment")
