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
from .constant import Constant
from .enum import Enum
from .offset import Offset
from .package import Package
from .scalar import Scalar
from .struct import Struct
from .union import Union

# Linting guards
assert Offset
assert Scalar

def __pt_dec(container):
    def __dec__(*args, package=None, **kwargs):
        def __inner__(cls):
            # Grab the annotations (if they exist)
            annotations = (
                cls.__annotations__ if hasattr(cls, "__annotations__") else {}
            )
            # Run through all of the variables
            fields  = {}
            ignored = 0
            for key, obj in vars(cls).items():
                # Ignore built-in/private types
                if key.startswith("__"): continue
                # See if there is a matching annotation?
                anno = annotations.get(key, None)
                # If there is a non-packtype object, it might need to be wrapped
                if anno == None or not isinstance(anno, Base):
                    # If it is an integer, wrap it as a constant
                    if isinstance(obj, int):
                        anno = Constant(value=obj, name=key)
                    # Otherwise, just ignore this
                    else:
                        print(f"{cls.__name__} ignoring field {key} of unknown type")
                        ignored += 1
                        continue
                # Otherwise, assign the name and value to the annotation
                else:
                    anno._pt_name = key
                    anno.assign(obj)
                # Take note of the field
                fields[key] = anno
            # Run through the annotations to catch non-valued attributes
            for key, anno in annotations.items():
                # Skip known entries
                if key in fields: continue
                # Assign the name to the annotation
                anno._pt_name = key
                # Attach unknown entries
                fields[key] = anno
            # If no legal fields are present, abort
            if ignored > 0:
                assert len(fields.keys()) > 0, f"No legal fields found for {cls.__name__}"
            # Use a cleaned-up docstring for the description
            desc = cls.__doc__
            if isinstance(desc, str):
                desc = " ".join([
                    x.strip() for x in desc.split("\n") if len(x.strip()) > 0
                ])
            # Form the container
            c_inst = container(cls.__name__, fields, desc=desc, *args, **kwargs)
            # If a package was provided, attach the container
            if package: package._pt_append(cls.__name__, c_inst)
            # Return the container
            return c_inst
        return __inner__
    return __dec__

enum    = __pt_dec(Enum)
package = __pt_dec(Package)
struct  = __pt_dec(Struct)
union   = __pt_dec(Union)
