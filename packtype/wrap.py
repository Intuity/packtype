# Copyright 2023, Peter Birch, mailto:peter@intuity.io
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

import dataclasses
import functools
import inspect
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from .array import ArraySpec
from .assembly import Base
from .primitive import Primitive


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


@functools.cache
def get_wrapper(base: Any, frame_depth: int = 1) -> Callable:
    def _wrapper(parent: Base | None = None, **kwds) -> Callable:
        def _inner(cls):
            # Work out the fields defined within the class
            cls_fields = set(dir(cls)).difference(dir(object))
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
            # Check fields
            for fname, fdef in dc_fields.items():
                base_type = fdef.type
                if isinstance(base_type, ArraySpec):
                    base_type = base_type.base
                # Check for acceptable base type
                if not isinstance(base_type, Primitive) and not issubclass(
                    base_type, Base | Primitive
                ):
                    raise BadFieldTypeError(
                        f"{cls.__name__}.{fname} is of an unsupported type "
                        f"{base_type.__name__}"
                    )
                # Map a missing value to None
                if isinstance(fdef.default, dataclasses._MISSING_TYPE):
                    fdef.default = None
                # Check if assignment allowed
                if fdef.default is not None and not fdef.type._PT_ALLOW_DEFAULT:
                    raise BadAssignmentError(
                        f"{cls.__name__}.{fname} cannot be assigned an initial "
                        f"value of {fdef.default}"
                    )
            # Check for supported attributes
            attrs = {}
            for key, value in kwds.items():
                # Skip certain keys
                if key in ("parent", ):
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
                cls.__name__,
                (base,),
                {
                    "__doc__": cls.__doc__,
                    "_PT_DEF": dc,
                    "_PT_ATTACH": [],
                    "_PT_ATTRIBUTES": attrs,
                    "_PT_SOURCE": (frame.f_code.co_filename, frame.f_lineno),
                },
            )
            # Reattach functions
            for fname in cls_funcs:
                setattr(imposter, fname, getattr(cls, fname))
            # Imposter construction
            imposter._pt_construct(parent, **attrs)
            # Register the imposter
            Registry.register(base, imposter)
            # Return the imposter as a substitute
            return imposter

        return _inner

    return _wrapper
