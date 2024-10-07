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

def _read_host(address: int) -> int:
    ptr = ctypes.cast(ctypes.c_void_p(address), ctypes.POINTER(ctypes.c_uint${bit_cadence}))
    return ptr[0]


async def _read_host_async(address: int) -> int:
    return _read_host(address)


async def _write_host(address: int, data: int) -> None:
    ptr = ctypes.cast(ctypes.c_void_p(address), ctypes.POINTER(ctypes.c_uint${bit_cadence}))
    ptr[0] = data


async def _write_host_async(address: int, data: int) -> None:
    _write_host(address, data)

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
    %for _, _, (name, field) in base()._pt_fields_msb_desc:
    ${name | tc.snake_case}: int = 0x${f"{int(field):X}"}
    %endfor ## _, _, (name, _) in base()._pt_fields_msb_desc

    def __int__(self) -> int:
        return self.pack()

    def pack(self) -> int:
        value = 0
    %for lsb, _, (name, field) in base()._pt_fields_msb_desc:
        value |= (self.${name | tc.snake_case} & 0x${f"{(1 << field._pt_width) - 1:X}"}) << ${lsb}
    %endfor ## lsb, _, (name, field) in base()._pt_fields_msb_desc
        return value

    @classmethod
    def unpack(cls, value: int) -> "${cls_name}${base.__name__ | tc.camel_case}":
        return cls(
    %for lsb, _, (name, field) in base()._pt_fields_msb_desc:
            ${name | tc.snake_case}=((value >> ${lsb}) & 0x${f"{(1 << field._pt_width) - 1:X}"}),
    %endfor ## lsb, _, (name, field) in base()._pt_fields_msb_desc
        )

%endfor ## base in base_types

# ==============================================================================
# Generic Register Abstractions
# ==============================================================================

class RegisterBase:

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


class SyncDataX2I(RegisterBase):
    def write(self, *args, **kwds) -> None:
        value = 0
        if args:
            assert not kwds, "Does not support both conditional and named arguments"
            assert len(args) == 1, "Only supports a single positional argument"
            try:
                value= int(args[0])
            except ValueError as e:
                raise ${cls_name}Error(f"Cannot cast {args[0]} to an integer") from e
            value = int(args[0])
        elif kwds:
            value = int(self._container(**kwds))
        else:
            raise Exception("Must provide positional or named arguments")
        self._parent._write_raw(self._offset, value)
    def read(self) -> dataclass:
        return self._container.unpack(self._parent._read_raw(self._offset))


class AsyncDataX2I(RegisterBase):
    async def write(self, *args, **kwds) -> None:
        value = 0
        if args:
            assert not kwds, "Does not support both conditional and named arguments"
            assert len(args) == 1, "Only supports a single positional argument"
            try:
                value= int(args[0])
            except ValueError as e:
                raise ${cls_name}Error(f"Cannot cast {args[0]} to an integer") from e
            value = int(args[0])
        elif kwds:
            value = int(self._container(**kwds))
        else:
            raise Exception("Must provide positional or named arguments")
        await self._parent._write_raw_async(self._offset, value)
    async def read(self) -> dataclass:
        return self._container.unpack(await self._parent._read_raw_async(self._offset))


class SyncDataI2X(RegisterBase):
    def read(self) -> dataclass:
        return self._container.unpack(self._parent._read_raw(self._offset))


class AsyncDataI2X(RegisterBase):
    async def read(self) -> dataclass:
        return self._container.unpack(await self._parent._read_raw_async(self._offset))


class FifoBase(RegisterBase):
    def __init__(self, level_offset: ${cls_name}Offset, *args, **kwds) -> None:
        super().__init__(*args, **kwds)
        self._level_offset = level_offset


class SyncFifoX2I(FifoBase):
    def push(self, *args, **kwds) -> None:
        value = 0
        if args:
            assert not kwds, "Does not support both conditional and named arguments"
            assert len(args) == 1, "Only supports a single positional argument"
            try:
                value= int(args[0])
            except ValueError as e:
                raise ${cls_name}Error(f"Cannot cast {args[0]} to an integer") from e
            value = int(args[0])
        elif kwds:
            value = int(self._container(**kwds))
        else:
            raise Exception("Must provide positional or named arguments")
        self._parent._write_raw(self._offset, value)
    def get_level(self) -> int:
        return self._parent._read_raw(self._level_offset)


class AsyncFifoX2I(FifoBase):
    async def push(self, *args, **kwds) -> None:
        value = 0
        if args:
            assert not kwds, "Does not support both conditional and named arguments"
            assert len(args) == 1, "Only supports a single positional argument"
            try:
                value= int(args[0])
            except ValueError as e:
                raise ${cls_name}Error(f"Cannot cast {args[0]} to an integer") from e
            value = int(args[0])
        elif kwds:
            value = int(self._container(**kwds))
        else:
            raise Exception("Must provide positional or named arguments")
        await self._parent._write_raw_async(self._offset, value)
    async def get_level(self) -> int:
        return await self._parent._read_raw_async(self._level_offset)


class SyncFifoI2X(FifoBase):
    def pop(self) -> dataclass:
        return self._container.unpack(self._parent._read_raw(self._offset))
    def get_level(self) -> int:
        return self._parent._read_raw(self._level_offset)


class AsyncFifoI2X(FifoBase):
    async def pop(self) -> dataclass:
        return self._container.unpack(await self._parent._read_raw_async(self._offset))
    async def get_level(self) -> int:
        return await self._parent._read_raw_async(self._level_offset)

# ==============================================================================
# Register Interface Class
# ==============================================================================

class ${cls_name}:
    """
    Class to interface with the ${cls_name} register file, allowing access to
    each register for read/write.

    :param base_address: Set the offset base address to access the register
                         file, defaults to zero
    :param use_async:    Whether to use asyncio access patterns
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
        use_async: bool = False,
        read_fn: Callable[[int, ], int] | None = None,
        write_fn: Callable[[int, int], None] | None = None,
    ) -> None:
        # Attach attributes
        self._base_address = base_address
        self._read_fn = read_fn or [_read_host, _read_host_async][use_async]
        self._write_fn = write_fn or [_write_host, _write_host_async][use_async]
        # Attach registers
%for reg in filter(lambda x: x._PT_BEHAVIOUR.is_primary, baseline):
<%
    behav  = reg._PT_BEHAVIOUR
    rname  = tc.underscore(reg._pt_fullname)
%>\
    %if behav in (Behaviour.CONSTANT, Behaviour.DATA_I2X, Behaviour.DATA_X2I):
<%      wname = f"Data{['I2X', 'X2I'][behav is Behaviour.DATA_X2I]}" %>\
        self.${rname} = (Async${wname} if use_async else Sync${wname})(
            name="${rname}",
            offset=${cls_name}Offset.${rname.upper()},
            parent=self,
            container=${cls_name}${type(reg).__name__ | tc.camel_case},
        )
    %elif behav in (Behaviour.FIFO_X2I, Behaviour.FIFO_I2X):
<%
        lvl   = reg._pt_paired[Behaviour.LEVEL]
        wname = f"Fifo{['I2X', 'X2I'][behav is Behaviour.FIFO_X2I]}"
%>\
        self.${rname} = (Async${wname} if use_async else Sync${wname})(
            name="${rname}",
            offset=${cls_name}Offset.${rname.upper()},
            level_offset=${cls_name}Offset.${lvl._pt_fullname.upper() | tc.underscore},
            parent=self,
            container=${cls_name}${type(reg).__name__ | tc.camel_case},
        )
    %else:
<%      raise Exception("Unsupported behaviour!") %>
    %endif
%endfor ## reg in filter(lambda x: x._PT_BEHAVIOUR.is_primary, baseline)

    def _read_raw(self, offset: ${cls_name}Offset) -> int:
        return self._read_fn(self._base_address + int(offset))

    async def _read_raw_async(self, offset: ${cls_name}Offset) -> int:
        return await self._read_fn(self._base_address + int(offset))

    def _write_raw(self, offset: int, data: ${cls_name}Offset) -> None:
        self._write_fn(self._base_address + int(offset), data)

    async def _write_raw_async(self, offset: int, data: ${cls_name}Offset) -> None:
        await self._write_fn(self._base_address + int(offset), data)
