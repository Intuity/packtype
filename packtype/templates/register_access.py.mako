<%doc>
Copyright 2023, Peter Birch, mailto:peter@intuity.io

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
</%doc>\
<%include file="header.mako" args="delim='#'" />\
<%namespace name="blocks" file="blocks.mako" />\
<%
cls_name = type(baseline).__name__
bit_cadence = baseline._PT_BIT_CADENCE
pfx_async = "async " if options.get("async", False) else ""
pfx_await = "await " if options.get("async", False) else ""
base_types = {x for x in baseline._pt_references() if x._PT_BASE is Register}
%>\

import ctypes
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Callable

# ==============================================================================
# Error Class
# ==============================================================================

class ${cls_name}Error(Exception):
    pass

# ==============================================================================
# Host-Memory Mapped Access Routines
# ==============================================================================

${pfx_async}def _read_host(address: int) -> int:
    ptr = ctypes.cast(ctypes.c_void_p(address), ctypes.POINTER(ctypes.c_uint${bit_cadence}))
    return ptr[0]


${pfx_async}def _write_host(address: int, data: int) -> None:
    ptr = ctypes.cast(ctypes.c_void_p(address), ctypes.POINTER(ctypes.c_uint${bit_cadence}))
    ptr[0] = data

# ==============================================================================
# Offset Enumeration
# ==============================================================================

class ${cls_name}Offset(IntEnum):
    """ Register address offsets for the ${cls_name} register file """
%for idx, reg in enumerate(baseline):
    ${reg._pt_fullname.upper() | tc.underscore} = 0x${f"{reg._pt_offset:X}"}
%endfor ## idx, reg in enumerate(baseline)

# ==============================================================================
# Register Format Containers
# ==============================================================================

class ${cls_name}Container:
    pass


%for base in sorted(base_types, key=lambda x: x.__name__):
@dataclass
class ${cls_name}${base.__name__ | tc.camel_case}(${cls_name}Container):
    %for _, _, (name, _) in base()._pt_fields_msb_desc:
    ${name | tc.snake_case}: int
    %endfor ## _, _, (name, _) in base()._pt_fields_msb_desc

    def __int__(self) -> int:
        return self.pack()

    def pack(self) -> int:
        value = 0
    %for _, lsb, (name, field) in base()._pt_fields_msb_desc:
        value |= (self.${name | tc.snake_case} & 0x${f"{(1 << field._pt_width) - 1:X}"}) << ${lsb}
    %endfor ## _, lsb, (name, field) in base()._pt_fields_msb_desc
        return value

    @classmethod
    def unpack(cls, value: int) -> "${cls_name}${base.__name__ | tc.camel_case}":
        return cls(
    %for _, lsb, (name, field) in base()._pt_fields_msb_desc:
            ${name | tc.snake_case}=((value >> ${lsb}) & 0x${f"{(1 << field._pt_width) - 1:X}"}),
    %endfor ## _, lsb, (name, field) in base()._pt_fields_msb_desc
        )

%endfor ## base in base_types

# ==============================================================================
# Generic Register Abstractions
# ==============================================================================

class DataX2I:

    def __init__(
        self,
        name: str,
        offset: ${cls_name}Offset,
        parent: Any,
        container: dataclass,
    ) -> None:
        self._name = name
        self._offset = offset
        self._parent = parent
        self._container = container

    ${pfx_async}def write(self, data: int | ${cls_name}Container) -> None:
        ${pfx_await}self._parent._write_raw(self._offset, int(data))

    ${pfx_async}def read(self) -> dataclass:
        return self._container.unpack(${pfx_await}self._parent._read_raw(self._offset))


class DataI2X:

    def __init__(
        self,
        name: str,
        offset: ${cls_name}Offset,
        parent: Any,
        container: dataclass,
    ) -> None:
        self._name = name
        self._offset = offset
        self._parent = parent
        self._container = container

    ${pfx_async}def write(self, data: int | ${cls_name}Container) -> None:
        raise ${cls_name}Error(f"Cannot write to {self._name} is it is of type {type(self).__name__}")

    ${pfx_async}def read(self) -> dataclass:
        return self._container.unpack(${pfx_await}self._parent._read_raw(self._offset))


class FifoX2I:

    def __init__(
        self,
        name: str,
        offset: ${cls_name}Offset,
        level_offset: ${cls_name}Offset,
        parent: Any,
        container: dataclass,
    ) -> None:
        self._name = name
        self._offset = offset
        self._parent = parent
        self._container = container

    ${pfx_async}def push(self, data: int | ${cls_name}Container) -> None:
        ${pfx_await}self._parent._write_raw(self._offset, int(data))

    ${pfx_async}def get_level(self) -> int:
        return ${pfx_await}self._parent._read_raw(self._offset)


class FifoI2X:

    def __init__(
        self,
        name: str,
        offset: ${cls_name}Offset,
        level_offset: ${cls_name}Offset,
        parent: Any,
        container: dataclass,
    ) -> None:
        self._name = name
        self._offset = offset
        self._parent = parent
        self._container = container

    ${pfx_async}def pop(self) -> dataclass:
        return self._container.unpack(${pfx_await}self._parent._read_raw(self._offset))

    ${pfx_async}def get_level(self) -> int:
        return ${pfx_await}self._parent._read_raw(self._offset)

# ==============================================================================
# Register Interface Class
# ==============================================================================

class ${cls_name}:
    """
    Class to interface with the ${cls_name} register file, allowing access to
    each register for read/write.

    :param base_address: Set the offset base address to access the register
                         file, defaults to zero
    :param read_fn:      Optional function to write to an address, if not provided
                         the default behaviour will be a read from the host's
                         memory map
    :param write_fn:     Optional function to read from an address, if not
                         provided the default behaviour will be a write to the
                         host's address map
    """

    def __init__(
        self,
        base_address: int = 0,
        read_fn: Callable[[int, ], int] = _read_host,
        write_fn: Callable[[int, int], None] = _write_host,
    ) -> None:
        # Attach attributes
        self._base_address = base_address
        self._read_fn = read_fn
        self._write_fn = write_fn
        # Attach registers
%for reg in filter(lambda x: x._PT_BEHAVIOUR.is_primary, baseline):
<%
    behav  = reg._PT_BEHAVIOUR
    rname  = tc.underscore(reg._pt_fullname)
%>\
    %if behav in (Behaviour.CONSTANT, Behaviour.DATA_I2X, Behaviour.DATA_X2I):
        self.${rname} = Data${["I2X", "X2I"][behav is Behaviour.DATA_X2I]}(
            "${rname}",
            ${cls_name}Offset.${rname.upper()},
            self,
            ${cls_name}${type(reg).__name__ | tc.camel_case},
        )
    %elif behav in (Behaviour.FIFO_X2I, Behaviour.FIFO_I2X):
<%      lvl = reg._pt_paired[Behaviour.LEVEL] %>\
        self.${rname} = Fifo${["I2X", "X2I"][behav is Behaviour.FIFO_X2I]}(
            "${rname}",
            ${cls_name}Offset.${rname.upper()},
            ${cls_name}Offset.${lvl._pt_fullname.upper() | tc.underscore},
            self,
            ${cls_name}${type(reg).__name__ | tc.camel_case},
        )
    %else:
<%      raise Exception("Unsupported behaviour!") %>
    %endif
%endfor ## reg in filter(lambda x: x._PT_BEHAVIOUR.is_primary, baseline)

    ${pfx_async}def _read_raw(self, offset: ${cls_name}Offset) -> int:
        return ${pfx_await}self._read_fn(self._base_address + int(offset))

    ${pfx_async}def _write_raw(self, offset: int, data: ${cls_name}Offset) -> None:
        ${pfx_await}self._write_fn(self._base_address + int(offset), data)
