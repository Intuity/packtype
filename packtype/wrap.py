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
from typing import Any, Callable

from .assembly import Base
from .primitive import Primitive

class MissingAnnotation(Exception):
    pass

class BadFieldType(Exception):
    pass

class BadAssignment(Exception):
    pass

class BadAttribute(Exception):
    pass

@functools.cache
def get_wrapper(base: Any) -> Callable:
    def _wrapper(**kwds) -> Callable:
        def _inner(cls):
            # Work out the fields defined within the class
            cls_fields = set(dir(cls)).difference(dir(object))
            # Filter out any dunder entries
            cls_fields = { x for x in cls_fields if not x.startswith("__") }
            # Filter out any functions
            cls_funcs = { x for x in cls_fields if callable(getattr(cls, x)) }
            cls_fields = cls_fields.difference(cls_funcs)
            # Process class with dataclass
            dc = dataclasses.dataclass()(cls)
            dc_fields = {x.name: x for x in dataclasses.fields(dc)}
            # Check for missing fields
            for field in cls_fields.difference(dc_fields.keys()):
                raise MissingAnnotation(f"{cls.__name__}.{field} is not annotated")
            # Check fields
            for fname, fdef in dc_fields.items():
                # Check for acceptable base type
                if not isinstance(fdef.type, Primitive) and not issubclass(fdef.type, (Base, Primitive)):
                    raise BadFieldType(
                        f"{cls.__name__}.{fname} is of an unsupported type "
                        f"{fdef.type.__name__}"
                    )
                # Check if assignment allowed
                if not isinstance(fdef.default, dataclasses._MISSING_TYPE) and not fdef.type._PT_ALLOW_DEFAULT:
                    raise BadAssignment(
                        f"{cls.__name__}.{fname} cannot be assigned an initial "
                        f"value of {fdef.default}"
                    )
            # Check for supported attributes
            attrs = {}
            for key, value in kwds.items():
                if key not in base._PT_ATTRIBUTES:
                    raise BadAttribute(f"Unsupported attribute '{key}' for {base.__name__}")
                _, accepted = base._PT_ATTRIBUTES[key]
                if (
                    (callable(accepted) and not accepted(value)) or
                    (isinstance(accepted, tuple) and value not in accepted)
                ):
                    raise BadAttribute(
                        f"Unsupported value '{value}' for attribute '{key}' "
                        f"for {base.__name__}"
                    )
                attrs[key] = value
            # Fill in default attributes
            for key, (default, _) in base._PT_ATTRIBUTES.items():
                if key not in attrs:
                    attrs[key] = default
            # Create imposter class
            imposter = type(
                cls.__name__,
                (base, ),
                { "__doc__": cls.__doc__,
                "_PT_DEF": dc,
                "_PT_ATTACH": [],
                "_PT_ATTRIBUTES": attrs }
            )
            # Reattach functions
            for fname in cls_funcs:
                setattr(imposter, fname, getattr(cls, fname))
            return imposter
        return _inner
    return _wrapper