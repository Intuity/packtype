import enum
import inspect
import math
from collections.abc import Iterable
from functools import partial
from textwrap import indent
from typing import Any, Self

from .array import ArraySpec, UnpackedArray
from .assembly import PackedAssembly
from .base import Base
from .enum import Enum
from .constant import Constant
from .packing import Packing
from .primitive import NumericPrimitive
from .scalar import Scalar
from .struct import Struct
from .wrap import build_from_fields, get_wrapper
from ordered_set import OrderedSet as OSet

# NOTE 1: Consider sign extension vs zero extension behaviours, i.e. do we want
#         to offer automatic field expansion?


class Behaviour(enum.Enum):
    """Enumerates the different types of register"""

    # Primary types
    CONSTANT = enum.auto()
    """A static value that cannot be altered"""
    DATA_X2I = enum.auto()
    """Data that is externally written and internally read"""
    DATA_I2X = enum.auto()
    """Data that is internally written and externally read"""
    FIFO_X2I = enum.auto()
    """FIFO that is externally filled and internally decanted"""
    FIFO_I2X = enum.auto()
    """FIFO that is internally filled and externally decanted"""
    # Second/paired types
    LEVEL = enum.auto()
    """A paired register carrying level for FIFO_X2I and FIFO_I2X behaviours"""

    @property
    def is_primary(self) -> bool:
        return self in (
            Behaviour.CONSTANT,
            Behaviour.DATA_X2I,
            Behaviour.DATA_I2X,
            Behaviour.FIFO_X2I,
            Behaviour.FIFO_I2X,
        )

    @property
    def is_secondary(self) -> bool:
        return self in (Behaviour.LEVEL,)

    @property
    def internal_read(self) -> bool:
        return self in (Behaviour.DATA_X2I, Behaviour.FIFO_X2I)

    @property
    def internal_read_strobe(self) -> bool:
        return self in (Behaviour.DATA_X2I,)

    @property
    def internal_read_stream(self) -> bool:
        return self in (Behaviour.FIFO_X2I,)

    @property
    def internal_write(self) -> bool:
        return self in (Behaviour.DATA_I2X, Behaviour.FIFO_I2X)

    @property
    def internal_write_strobe(self) -> bool:
        return self in (Behaviour.DATA_I2X,)

    @property
    def internal_write_stream(self) -> bool:
        return self in (Behaviour.FIFO_I2X,)

    @property
    def external_read(self) -> bool:
        return self in (
            Behaviour.CONSTANT,
            Behaviour.DATA_X2I,
            Behaviour.DATA_I2X,
            Behaviour.FIFO_I2X,
        )

    @property
    def external_write(self) -> bool:
        return self in (Behaviour.DATA_X2I, Behaviour.FIFO_X2I)


class Register(PackedAssembly):
    """Defines a single register with a behaviour, width, and alignment"""

    # Allow both constants and scalars to be assigned values
    _PT_ALLOW_DEFAULTS: list[type[Base]] = [Constant, Enum, Scalar, Struct]
    # Detail custom attributes that registers offer
    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {
        "behaviour": (Behaviour.CONSTANT, list(Behaviour)),
        "packing": (Packing.FROM_LSB, [Packing.FROM_LSB, Packing.FROM_MSB]),
        "width": (-1, lambda x: int(x) > 0),
        "align": (0, lambda x: int(x) >= 0),
        # Used for FIFOs
        "depth": (None, lambda x: int(x) >= 0),
    }
    _PT_BEHAVIOUR: Behaviour
    _PT_ALIGN: int
    _PT_BYTE_SIZE: int
    _PT_PAIRED: dict[Behaviour, Self]
    # Used for FIFOs
    _PT_DEPTH: int = 4

    def __init__(
        self,
        name: str | None = None,
        index: int | None = None,
        offset: int = 0,
    ) -> None:
        super().__init__()
        self.__name = name or type(self).__name__.lower()
        self._pt_index = index
        self._pt_offset = offset
        self._pt_paired = {
            x: y(name=x.name.lower()) for x, y in self._PT_PAIRED.items()
        }
        for paired in self._pt_paired.values():
            paired._PT_PARENT = self

    def _pt_name(self) -> str:
        return self.__name

    def __iter__(self) -> Iterable[Self]:
        yield self
        yield from self._pt_paired.values()

    @property
    def _pt_path(self) -> Iterable[str]:
        if self._pt_parent:
            yield from self._pt_parent._pt_path
        if self.__name is not None:
            yield self.__name
        if self._pt_index is not None:
            yield self._pt_index

    @property
    def _pt_fullname(self) -> str:
        return ".".join(map(str, self._pt_path))

    def __repr__(self) -> str:
        chunks = [
            (
                f"0x{self._pt_offset:04X} <{self._PT_BASE.__name__}::"
                f"{type(self).__name__}> {self.__name} ({self._pt_fullname})\n"
            )
            + indent(super().__str__(), "  ")
        ]
        for sub in self._pt_paired.values():
            chunks.append(str(sub))
        return "\n".join(chunks)

    def __str__(self) -> str:
        return self.__repr__()

    @classmethod
    def _pt_construct(
        cls,
        parent: Base,
        behaviour: Behaviour,
        packing: Packing,
        width: int | None,
        align: int | None,
        depth: int | None,
    ):
        super()._pt_construct(parent, packing, width)
        cls._PT_BEHAVIOUR = behaviour
        cls._PT_ALIGN = int(align or 0)
        cls._PT_BYTE_SIZE = (cls._PT_WIDTH + 7) // 8
        cls._PT_PAIRED = {}
        if depth is not None and behaviour not in (Behaviour.FIFO_I2X, Behaviour.FIFO_X2I):
            raise Exception(f"Depth is not supported for {behaviour.name}")
        elif depth is not None:
            cls._PT_DEPTH = depth


register = get_wrapper(Register)


class Group(Base):
    """Describes a group of registers that can be references by a register file"""

    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {
        "width": (None, lambda x: x is None or int(x) > 0),
        "align": (None, lambda x: x is None or int(x) > 0),
        "spacing": (None, lambda x: x is None or int(x) > 0),
    }
    _PT_WIDTH: int | None
    _PT_ALIGN: int | None
    _PT_OFFSETS: dict[str, int]
    _PT_BYTE_SIZE: int
    _PT_BIT_CADENCE: int
    _PT_BYTE_CADENCE: int

    def __init__(
        self,
        name: str | None = None,
        index: int | None = None,
        offset: int = 0,
        cadence: int = 4,
    ) -> None:
        super().__init__()
        self._pt_name = name
        self._pt_index = index
        self._pt_offset = offset
        self._pt_fields: dict[Group | Register, str] = {}

        def _lookup(offset: int, name: str, idx: int):
            _, _, sub_offset = self._PT_OFFSETS[name, idx]
            return [], {"name": name, "offset": offset + sub_offset, "index": idx}

        for fname, ftype, _ in self._pt_definitions():
            if isinstance(ftype, ArraySpec):
                finst = ftype.as_unpacked(_pt_per_inst=partial(_lookup, offset, fname))
                for sub in finst:
                    sub._PT_PARENT = self
                    if sub._PT_BASE is Register:
                        for pbehav, preg in sub._pt_paired.items():
                            _, _, prd_offset = self._PT_OFFSETS[(fname, pbehav), 0]
                            preg._pt_offset = sub._pt_offset + prd_offset
            elif ftype._PT_BASE in (Group, Register):
                _, _, sub_offset = self._PT_OFFSETS[fname, 0]
                finst = ftype(name=fname, index=None, offset=offset + sub_offset)
                finst._PT_PARENT = self
                if ftype._PT_BASE is Register:
                    for pbehav, preg in finst._pt_paired.items():
                        _, _, prd_offset = self._PT_OFFSETS[(fname, pbehav), 0]
                        preg._pt_offset = finst._pt_offset + prd_offset
            else:
                raise Exception(f"Unsupported type: {ftype}")
            setattr(self, fname, finst)
            self._pt_fields[finst] = fname

    def __iter__(self) -> Register | Self:
        for finst in self._pt_fields.keys():
            if isinstance(finst, UnpackedArray):
                for sub in finst:
                    yield from sub
            else:
                yield from finst

    def __repr__(self) -> str:
        lines = []
        desc = f"<{self._PT_BASE.__name__}::{type(self).__name__}>"
        if self._pt_name:
            desc = f"{desc} {self._pt_name}"
        if self._pt_index is not None:
            desc = f"{desc}[{self._pt_index}]"
        lines.append(desc)
        for finst in self._pt_fields.keys():
            if isinstance(finst, UnpackedArray):
                for sub in finst:
                    lines.append(indent(str(sub), "  "))
            else:
                lines.append(indent(str(finst), "  "))
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def _pt_path(self) -> Iterable[str]:
        if self._pt_parent:
            yield from self._pt_parent._pt_path
        if self._pt_name is not None:
            yield self._pt_name
        if self._pt_index is not None:
            yield self._pt_index

    @property
    def _pt_fullname(self) -> str:
        return ".".join(map(str, self._pt_path))

    @classmethod
    def _pt_construct(
        cls, parent: Base, width: int | None, align: int | None, spacing: int | None
    ):
        # Process assignments
        cls._PT_WIDTH = None if width is None else int(width)
        cls._PT_ALIGN = None if align is None else int(align)
        cls._PT_SPACING = None if spacing is None else int(spacing)
        cls._PT_OFFSETS: dict[str, (int, int)] = {}
        cls._PT_BYTE_SIZE = 0
        cls._PT_BIT_CADENCE = 0
        cls._PT_BYTE_CADENCE = 0
        # Check through fields
        for fname, ftype, _ in cls._pt_definitions():
            fbase = ftype.base if isinstance(ftype, ArraySpec) else ftype
            # Sanity check only groups and registers are being attached
            if fbase._PT_BASE not in (Register, Group):
                raise Exception(f"Cannot attach {fname} of type {fbase.__name__}")
            # Check for legal primary registers
            if fbase._PT_BASE is Register and not fbase._PT_BEHAVIOUR.is_primary:
                raise Exception(
                    f"{fbase._PT_BEHAVIOUR.name} is not a legal primary behaviour "
                    f"for register {fbase.__name__}"
                )
            # Check the width constraint
            if cls._PT_WIDTH is None:
                cls._PT_WIDTH = fbase._PT_WIDTH
            elif fbase._PT_WIDTH is not None and cls._PT_WIDTH < fbase._PT_WIDTH:
                raise Exception(
                    f"Incompatibility between {cls._PT_BASE.__name__} {cls.__name__} "
                    f"of width {cls._PT_WIDTH} and field {fname} of width "
                    f"{fbase._PT_WIDTH}"
                )
            # For FIFO behaviours, add a level register
            if fbase._PT_BASE is Register and fbase._PT_BEHAVIOUR in (
                Behaviour.FIFO_I2X,
                Behaviour.FIFO_X2I,
            ):
                # TODO @intuity: Allow configurable level
                fbase._PT_PAIRED[Behaviour.LEVEL] = build_from_fields(
                    base=Register,
                    cname=fbase.__name__ + "Level",
                    fields={"value": (Scalar[math.ceil(math.log2(fbase._PT_DEPTH+1))], None)},
                    kwds={"behaviour": Behaviour.LEVEL},
                    parent=fbase,
                )
            # Insert a placeholder entry to offsets
            dimension = ftype.dimension if isinstance(ftype, ArraySpec) else 1
            for idx in range(dimension):
                cls._PT_OFFSETS[fname, idx] = (
                    fbase._PT_BYTE_SIZE,
                    fbase._PT_ALIGN or 1,
                    0,
                )
                if fbase._PT_BASE is Register:
                    for pbehav, ptype in fbase._PT_PAIRED.items():
                        cls._PT_OFFSETS[(fname, pbehav), idx] = (
                            ptype._PT_BYTE_SIZE,
                            ptype._PT_ALIGN or 1,
                            0,
                        )
        # Work out what a sensible power of two placement would be
        cadence_bits = 1 << (cls._PT_WIDTH - 1).bit_length()
        cadence_byte = (cadence_bits + 7) // 8
        # Calculate offset placements
        byte_offset = 0
        for (name, idx), (byte_size, align, _) in cls._PT_OFFSETS.items():
            # Bump offset to the nearest legal alignment
            if (dist := (byte_offset % align)) != 0:
                byte_offset += int(align - dist)
            # Encode the placement
            cls._PT_OFFSETS[name, idx] = (byte_size, align, int(byte_offset))
            # Bump the offset by the cadence
            byte_offset += cadence_byte * (
                (byte_size + cadence_byte - 1) // cadence_byte
            )
        # Remember the final offset
        cls._PT_BYTE_SIZE = byte_offset
        cls._PT_BIT_CADENCE = cadence_bits
        cls._PT_BYTE_CADENCE = cadence_byte


group = get_wrapper(Group)


class File(Group):
    """Top-level of the register file"""

    @property
    def _pt_max_offset(self) -> int:
        return max(x._pt_offset for x in self)

    @classmethod
    def _pt_foreign(cls):
        # Get all referenced types
        all_refs = cls._pt_references()
        # Exclude directly attached types
        foreign = all_refs.difference(OSet(cls._PT_ATTACH).union(cls._pt_field_types()))

        # Exclude non-typedef primitives
        def _is_a_type(obj: Any) -> bool:
            # If this is an ArraySpec, refer to the encapsulated type
            if isinstance(obj, ArraySpec):
                obj = obj.base
            if obj._PT_BASE in (Group, Register):
                return False
            # If it's not a primitive, immediately accept
            if inspect.isclass(obj) and not issubclass(obj, NumericPrimitive):
                return True
            # If not attached to a different package, accept
            return (
                obj._PT_ATTACHED_TO is not None and type(obj._PT_ATTACHED_TO) is not cls
            )

        return OSet(filter(_is_a_type, foreign))


file = get_wrapper(File)
