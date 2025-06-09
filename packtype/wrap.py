# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import dataclasses
import functools
import inspect
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from .alias import Alias
from .array import ArraySpec
from .assembly import Base
from .primitive import NumericPrimitive
from ordered_set import OrderedSet as OSet

class MissingAnnotationError(Exception):
    pass


class BadFieldTypeError(Exception):
    pass


class BadAssignmentError(Exception):
    pass


class BadAttributeError(Exception):
    pass


class Registry:
    ENTRIES: dict[type[Base], list[type[Base] | Base]] = defaultdict(list)

    @classmethod
    def register(cls, root: type[Base], item: Base) -> None:
        cls.ENTRIES[root].append(item)

    @classmethod
    def query(cls, root: type[Base]) -> Base:
        yield from cls.ENTRIES[root]

    @classmethod
    def reset(cls) -> None:
        cls.ENTRIES.clear()


def build_from_fields(
    base: Any,
    cname: str,
    fields: dict[str, tuple[str, Any]],
    kwds: dict[str, Any],
    frame_depth: int = 1,
    doc_str: str | None = None,
    cls_funcs: dict[str, Callable[..., Any]] | None = None,
    parent: Any | None = None,
) -> Any:
    # Check fields
    for fname, (ftype, default) in fields.items():
        real_type = ftype.base if isinstance(ftype, ArraySpec) else ftype
        # Unwrap alias types
        if issubclass(real_type, Alias):
            real_type = real_type._PT_ALIAS
        # Check for acceptable base type
        if not isinstance(real_type, NumericPrimitive) and not issubclass(
            real_type, Base | NumericPrimitive
        ):
            raise BadFieldTypeError(
                f"{cname}.{fname} is of an unsupported type {real_type.__name__}"
            )
        # Map a missing value to None
        if isinstance(default, dataclasses._MISSING_TYPE):
            fields[fname] = (ftype, None)
        # Check if assignment allowed
        # NOTE: The subclass check is necessary for scalar/constant specialisations
        elif default is not None and real_type not in base._PT_ALLOW_DEFAULTS and not any(issubclass(real_type, x) for x in base._PT_ALLOW_DEFAULTS):
            raise BadAssignmentError(
                f"{cname}.{fname} cannot be assigned an initial value of {default} "
                f"within a base type of {base.__name__}"
            )
    # Check for supported attributes
    attrs = {}
    for key, value in kwds.items():
        # Skip certain keys
        if key in ("parent",):
            continue
        # Check if supported by the type
        if key not in base._PT_ATTRIBUTES:
            raise BadAttributeError(
                f"Unsupported attribute '{key}' for {base.__name__}"
            )
        # Check value is acceptable
        _, accepted = base._PT_ATTRIBUTES[key]
        if (callable(accepted) and not accepted(value)) or (
            isinstance(accepted, tuple) and value not in accepted
        ):
            raise BadAttributeError(
                f"Unsupported value '{value}' for attribute '{key}' "
                f"for {base.__name__}"
            )
        # Store attribute
        attrs[key] = value
    # Fill in default attributes
    for key, (default, _) in base._PT_ATTRIBUTES.items():
        if key not in attrs:
            attrs[key] = default
    # Determine source
    frame = inspect.currentframe()
    for _ in range(frame_depth):
        frame = frame.f_back
    # Create imposter class
    imposter = type(
        cname,
        (base,),
        {
            "__doc__": doc_str,
            "_PT_DEF": fields,
            "_PT_ATTACH": [],
            "_PT_ATTRIBUTES": attrs,
            "_PT_SOURCE": (frame.f_code.co_filename, frame.f_lineno),
            "_PT_BASE": base,
        },
    )
    # Reattach functions
    for fname, func in (cls_funcs or {}).items():
        setattr(imposter, fname, func)
    # Imposter construction
    imposter._pt_construct(parent, **attrs)
    # Register the imposter
    Registry.register(base, imposter)
    # Return the imposter as a substitute
    return imposter


@functools.cache
def get_wrapper(base: Any, frame_depth: int = 1) -> Callable:
    def _wrapper(parent: Base | None = None, **kwds) -> Callable:
        def _inner(cls):
            # Work out the fields defined within the class
            cls_fields = OSet(dir(cls)).difference(dir(object))
            # Filter out any dunder entries
            cls_fields = {x for x in cls_fields if not x.startswith("__")}
            # Filter out any functions
            cls_funcs = {x for x in cls_fields if callable(getattr(cls, x))}
            cls_fields = cls_fields.difference(cls_funcs)
            # Process class with dataclass
            dc = dataclasses.dataclass(init=False)(cls)
            dc_fields = {x.name: x for x in dataclasses.fields(dc)}
            # Check for missing fields
            for field in cls_fields.difference(dc_fields.keys()):
                raise MissingAnnotationError(f"{cls.__name__}.{field} is not annotated")
            # Construct the imposter
            return build_from_fields(
                base=base,
                cname=cls.__name__,
                fields={x: (y.type, y.default) for x, y in dc_fields.items()},
                kwds=kwds,
                frame_depth=frame_depth,
                doc_str=cls.__doc__,
                cls_funcs={x: getattr(cls, x) for x in cls_funcs},
                parent=parent,
            )

        return _inner

    return _wrapper
