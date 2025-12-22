# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import inspect
import math

import tabulate

from ..types.alias import Alias
from ..types.array import ArraySpec, PackedArray, UnpackedArray
from ..types.assembly import PackedAssembly
from ..types.base import Base
from ..types.enum import Enum
from ..types.numeric import Numeric
from ..types.primitive import NumericType
from ..types.scalar import ScalarType
from ..types.union import Union


def clog2(x: int) -> int:
    """
    Calculate the ceiling of the base-2 logarithm of x.
    :param x: The integer to calculate the logarithm of
    :return: The ceiling of the base-2 logarithm of x
    """
    assert x > 0, "Input must be a positive integer."
    return math.ceil(math.log2(x))


def get_width(
    ptype: type[PackedAssembly | Enum | NumericType | Union] | PackedAssembly | NumericType | Union,
) -> int:
    """
    Get the width of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The width in bits of the Packtype definition
    """
    if isinstance(ptype, PackedAssembly | Enum | NumericType | Union | PackedArray | ArraySpec):
        return ptype._pt_width
    elif issubclass(ptype, PackedAssembly | Enum | NumericType | Union):
        return ptype._PT_WIDTH
    elif issubclass(ptype, Alias):
        return get_width(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_name(ptype: type[Base] | Base) -> str:
    """
    Get the name of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The name of the Packtype definition
    """
    # If an array instance is passed, unwrap it to get the spec
    if isinstance(ptype, PackedArray | UnpackedArray):
        ptype = ptype._pt_spec
    # For an array spec...
    if isinstance(ptype, ArraySpec):
        # If it is associated to a package, use the type name it is declared with
        if ptype._PT_ATTACHED_TO is not None:
            return ptype._PT_ATTACHED_TO._PT_FIELDS[ptype]
        # Otherwise, raise an exception
        raise TypeError(f"Cannot determine a name for nested array spec {ptype}")
    elif isinstance(ptype, ScalarType) or (
        inspect.isclass(ptype) and issubclass(ptype, ScalarType)
    ):
        ptype = ptype if inspect.isclass(ptype) else type(ptype)
        return ptype._PT_ATTACHED_TO._PT_FIELDS[ptype]
    elif isinstance(ptype, Base) or (inspect.isclass(ptype) and issubclass(ptype, Base)):
        return ptype._pt_name()
    elif issubclass(ptype, Alias):
        return get_name(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_package(ptype: type[Base] | Base) -> type[Base] | None:
    """
    Get the package a Packtype definition is attached to, if the type is not
    associated to a package then None will be returned
    :param ptype: The Packtype definition to inspect
    :return: The Package to which this type is attached
    """
    if not isinstance(ptype, Base | ArraySpec) and not (
        inspect.isclass(ptype) and issubclass(ptype, Base)
    ):
        raise TypeError(f"{ptype} is not a Packtype definition")
    return ptype._PT_ATTACHED_TO


def get_doc(ptype: type[Base] | Base) -> str:
    """
    Get the docstring of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The docstring of the Packtype definition
    """
    if isinstance(ptype, Base) or issubclass(ptype, Base):
        return ptype.__doc__ or ""
    elif issubclass(ptype, Alias):
        return get_doc(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def get_source(ptype: type[Base] | Base) -> tuple[str, int]:
    """
    Get the name of a Packtype definition
    :param ptype: The Packtype definition to inspect
    :return: The source file and line number of the Packtype definition
    """
    if isinstance(ptype, Base) or issubclass(ptype, Base):
        return ptype._PT_SOURCE
    elif issubclass(ptype, Alias):
        return get_source(ptype._PT_ALIAS)
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def is_signed(ptype: type[NumericType] | NumericType) -> bool:
    """
    Check if a Packtype definition is signed
    :param ptype: The Packtype definition to check
    :return: True if the definition is signed, False otherwise
    """
    if isinstance(ptype, NumericType):
        return ptype._pt_signed
    elif issubclass(ptype, NumericType):
        return ptype._PT_SIGNED
    else:
        raise TypeError(f"{ptype} is not a Packtype definition")


def unpack[T: Base](ptype: type[T], value: int) -> T:
    """
    Unpack a value into a Packtype definition
    :param ptype: The Packtype definition to unpack into
    :param value: The value to unpack
    :return: An instance of the Packtype definition with the unpacked value
    """
    if isinstance(ptype, ArraySpec):
        return ptype._pt_unpack(value)
    if not inspect.isclass(ptype):
        raise TypeError(f"{ptype} is an instance of a Packtype definition")
    if not issubclass(ptype, Base):
        raise TypeError(f"{ptype} is not a Packtype definition")
    if issubclass(ptype, Numeric):
        return ptype._pt_unpack(value)

    raise TypeError(f"{ptype} (type {type(ptype)}) does not support unpacking")


def pack(pinst: Base) -> int:
    """
    Pack an instance of a Packtype definition into an integer
    :param pinst: The instance of the Packtype definition to pack
    :return: The packed value as an integer
    """
    if inspect.isclass(pinst):
        raise TypeError(f"{pinst} is not an instance of a Packtype definition")
    return int(pinst)


def copy[T: Base](pinst: T) -> T:
    """
    Safely copy a Packtype instance

    This is also more performant than using copy.deepcopy() on the packtype objects.

    Use unpack and pack to create a new instance via the packed integer
    """
    # Special case for arrays as type(pinst) is a Packed Array not an array spec
    if isinstance(pinst, PackedArray):
        return unpack(pinst._pt_spec, pack(pinst))
    return unpack(type(pinst), pack(pinst))


def is_scalar(ptype: type[Base] | Base) -> bool:
    """
    Check if a Packtype definition is a scalar type
    :param ptype: The Packtype definition to check
    :return: True if the definition is a scalar type, False otherwise
    """
    return isinstance(ptype, ScalarType) or (
        inspect.isclass(ptype) and issubclass(ptype, ScalarType)
    )


def diff_table(value_a: type[Base], value_b: type[Base], verbose: bool = False) -> str:
    """
    Generate a diff between two Packtype instances. This is a recursive function
    that walks through the hierarchy and compares all fields, tabulating where
    differences occur.

    :param value_a: First item to be compared
    :param value_b: Second item to be compared
    :param verbose: Show all fields in complex objects and do not filter matching
                    objects (default: False)
    :return: A tabulate table containing differing fields. If the objects are the
             same an empty string is returned. This function should not be used
             to check the equality of two objects as it is orders of magnitude
             slower than the __eq__ operation added to all Numeric types
    """
    # Check that the values are the same type
    if not isinstance(value_b, type(value_a)):
        raise TypeError("Value A and Value B must be the same class")
    if value_a == value_b:
        return ""
    diff_struct = diff(value_a, value_b, verbose)
    return tabulate.tabulate(
        tabular_data=diff_struct,
        headers="keys",
        tablefmt="grid",
        colalign=("left", "center", "center", "center"),
    )


def _format_value(value: type[Base] | Base) -> str:
    """
    Format a Packtype value for display in diffs

    :param value: The Packtype value to format
    :return: The formatted string
    """
    if isinstance(value, Enum):
        return str(value)
    else:
        # Max digits is enough to show 64 bits in hex before truncating
        max_digits = 21
        int_value = int(value)
        int_str = str(int_value)
        # Get top digits of int
        int_str = int_str[:max_digits] + ("..." if len(int_str) > max_digits else "")
        hex_str = f"0x{int_value:_X}"
        # Get top digits of hex value
        hex_str = hex_str[:max_digits] + ("..." if len(hex_str) > max_digits else "")
        return f"{int_str}\n{hex_str}"


def diff(
    value_a: type[Base], value_b: type[Base], verbose: bool = False, _path: list[str] | None = None
) -> dict[str, list[str | int | Enum]]:
    """
    A recursive function to generate a diff between two Packtype instances.
    :param value_a: Item to be compared
    :param value_b: Other item to be compared
    :param verbose: Show all fields in complex objects and do not filter matching objects
    :param _path: A list of strings that can be joined with a '.' to represent the current
                  field path in the recursion
    :return: A dictionary containing fields of: Member name, Value A, Value B and "Diff"
    """
    # Check that the values are the same type
    diff_dict = {"Member name": [], "Value A": [], "Value B": [], "Diff": []}

    if value_a.__class__ != value_b.__class__:
        raise TypeError(
            "Value A and Value B must be the same class,"
            f" got {value_a.__class__} and {value_b.__class__}"
        )
    # Initialize the name string to the class name if not provided
    _path = _path[:] if _path is not None else [get_name(value_a)]
    # Return early if the values are the same and not verbose diff
    if value_a == value_b and not verbose:
        return diff_dict
    # Add the components to the diff entry
    diff_dict["Member name"].append(".".join(_path))
    diff_dict["Value A"].append(_format_value(value_a))
    diff_dict["Value B"].append(_format_value(value_b))
    diff_dict["Diff"].append("Y" if value_a != value_b else " ")
    # Recurse to get subfields for complex types
    if isinstance(value_a, PackedAssembly | Union):
        # Complex assembly comparision
        for (a_subfield, a_name), b_subfield in zip(
            value_a._pt_fields.items(),
            value_b._pt_fields.keys(),
            strict=False,
        ):
            if a_subfield != b_subfield or verbose:
                sub_diff = diff(
                    a_subfield,
                    b_subfield,
                    verbose,
                    _path=[*_path, a_name],
                )
                for key in diff_dict.keys():
                    diff_dict[key].extend(sub_diff[key])
    elif isinstance(value_a, (PackedArray | UnpackedArray)):
        if len(value_a) != len(value_b):
            raise ValueError("Cannot diff arrays of different lengths")
        # Array comparison
        for idx, (a_element, b_element) in enumerate(zip(value_a, value_b, strict=False)):
            if a_element != b_element or verbose:
                element_path = _path.copy()
                element_path[-1] += f"[{idx}]"
                sub_diff = diff(
                    a_element,
                    b_element,
                    verbose,
                    _path=element_path,
                )
                for key in diff_dict.keys():
                    diff_dict[key].extend(sub_diff[key])

    return diff_dict
