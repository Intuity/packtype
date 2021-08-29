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
from .scalar import Scalar
from .struct import Struct
from .union import Union

def __pt_dec(container):
    def __dec__(*args, **kwargs):
        def __inner__(cls):
            # Run through all of the variables
            fields = {}
            for key, obj in vars(cls).items():
                # Ignore built-in/private types
                if key.startswith("__"): continue
                # See if there is a matching annotation?
                anno = cls.__annotations__.get(key, None)
                # If there is a non-packtype object, it might need to be wrapped
                if anno == None or not isinstance(anno, Base):
                    # If it is an integer, wrap it as a constant
                    if isinstance(obj, int):
                        anno = Constant(value=obj, name=key)
                    # Otherwise, just ignore this
                    else:
                        print(f"{cls.__name__} ignoring field {key} of unknown type")
                        continue
                # Otherwise, assign the name and value to the annotation
                else:
                    anno.name = key
                    anno.assign(obj)
                # Take note of the field
                fields[key] = anno
            # Run through the annotations to catch non-valued attributes
            for key, anno in cls.__annotations__.items():
                # Skip known entries
                if key in fields: continue
                # Assign the name to the annotation
                anno.name = key
                # Attach unknown entries
                fields[key] = anno
            # Form the container
            return container(cls.__name__, fields, *args, **kwargs)
        return __inner__
    return __dec__

enum   = __pt_dec(Enum)
struct = __pt_dec(Struct)
union  = __pt_dec(Union)
