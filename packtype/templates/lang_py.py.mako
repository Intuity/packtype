<%doc>
Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk

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

from enum import IntEnum

# ==============================================================================
# Constants
# ==============================================================================

%for obj in filter(lambda x: isinstance(x, Constant), package._pt_values()):
# ${obj.name.upper()}${tc.opt_desc(obj, " :")}
${obj.name.upper()} = 0x${f"{obj.value:08X}"}
%endfor ## obj in filter(lambda x: isinstance(x, Constant), package._pt_values())

# ==============================================================================
# Enumerations
# ==============================================================================

%for obj in filter(lambda x: isinstance(x, Enum), package._pt_values()):
${blocks.section(obj, delim="#", style="pascal")}
class ${obj._pt_name}(IntEnum):
    %for field in obj._pt_values():
    ${tc.snake_case(field._pt_name).upper()} = ${field.value}
    %endfor ## field in obj._pt_values()

%endfor ## obj in filter(lambda x: isinstance(x, Enum), package._pt_values())
# ==============================================================================
# Data Structures
# ==============================================================================

%for obj in filter(lambda x: isinstance(x, Struct), package._pt_values()):
${blocks.section(obj, delim="#", style="pascal")}
class ${obj._pt_name}:
    %if obj._pt_desc:
<%      desc = obj._pt_desc %>\
    """
        %while desc:
    ${desc[:76]}
<%          desc = desc[76:] %>\
        %endwhile
    """
    %endif

    def __init__(
        self,
        _pt_value=None,
        _pt_union=None,
        _pt_parent=None,
    %for field in sorted(obj._pt_values(), key=lambda x: x._pt_lsb):
        ${field._pt_name | tc.snake_case}=\
        %if isinstance(field, Instance) and isinstance(field._pt_container, Enum):
${field._pt_container._pt_name}.${list(field._pt_keys())[0]},
        %elif isinstance(field, Array) and isinstance(field._pt_container, Enum):
<%          val_name = f"{field._pt_container._pt_name}.{list(field._pt_keys())[0]}" %>\
[${", ".join([val_name] * field._pt_count)}],
        %elif isinstance(field, Array):
[${", ".join(["0"] * field._pt_count)}],
        %else:
0,
        %endif
    %endfor
    ):
        # Declare fields
    %for field in sorted(obj._pt_values(), key=lambda x: x._pt_lsb):
        %if isinstance(field, Array):
        self.__${field._pt_name} = []
        %endif
        %for idx in range(field._pt_count if isinstance(field, Array) else 1):
<%
            idx_sfx = f"[{idx}]" if isinstance(field, Array) else ""
            name = f"self.__{tc.snake_case(field._pt_name)}" + idx_sfx
%>\
            %if isinstance(field, Scalar):
        ${name} = ${field._pt_name | tc.snake_case}
            %elif isinstance(field._pt_container, (Struct, Union)):
        ${name} = ${field._pt_container._pt_name}(_pt_value=${field._pt_name | tc.snake_case}${idx_sfx}, _pt_parent=self)
            %elif isinstance(field._pt_container, Enum):
        ${name} = ${field._pt_container._pt_name}(${field._pt_name | tc.snake_case}${idx_sfx})
            %endif
        %endfor
    %endfor
        # Keep track of parent and union variables
        self.__pt_union  = _pt_union
        self.__pt_parent = _pt_parent
        # If a value was provided, decode it
        if _pt_value is not None:
            self.unpack(_pt_value, force=True)

    def _pt_updated(self, child):
        if self.__pt_parent:
            return self.__pt_parent._pt_updated(self)

    %for field in sorted(obj._pt_values(), key=lambda x: x._pt_lsb):
    @property
    def ${field._pt_name}(self):
        return self.__${field._pt_name}

        %if isinstance(field, Array):
    def set_${field._pt_name}(self, index, value):
        %else:
    @${field._pt_name}.setter
    def ${field._pt_name}(self, value):
        %endif
<%      idx_sfx = "[index]" if isinstance(field, Array) else "" %>\
        # Update the value
        %if isinstance(field, Scalar):
        self.__${field._pt_name | tc.snake_case}${idx_sfx} = value
        %elif isinstance(field._pt_container, (Struct, Union)):
        self.__${field._pt_name | tc.snake_case}${idx_sfx}.unpack(value)
        %elif isinstance(field._pt_container, Enum):
        self.__${field._pt_name | tc.snake_case}${idx_sfx} = ${field._pt_container._pt_name}(value)
        %endif
        # Notify parent of update
        if self.__pt_parent:
            self.__pt_parent._pt_updated(self)

    %endfor
    def pack(self):
        """ Pack ${obj._pt_name} into a ${int(obj._pt_width)} bit scalar

        Returns: A packed scalar value
        """
        scalar = 0
    %for field in sorted(obj._pt_values(), key=lambda x: x._pt_lsb):
<%      fname = f"self.__{tc.snake_case(field._pt_name)}" %>\
        %if isinstance(field, Scalar):
        scalar |= (${fname} & 0x${f"{field._pt_mask:X}"}) << ${field._pt_lsb}
        %elif isinstance(field, Array):
<%
            fmask = int(field._pt_container._pt_mask)
            fwidth = int(field._pt_container._pt_width)
%>\
            %for idx in range(field._pt_count):
<%              lsb = field._pt_lsb + fwidth * idx %>\
                %if isinstance(field._pt_container, (Struct, Union)):
        scalar |= (${fname}[${idx}].pack() & 0x${f"{fmask:X}"}) << ${lsb}
                %elif isinstance(field._pt_container, Enum):
        scalar |= (int(${fname}[${idx}]) & 0x${f"{fmask:X}"}) << ${lsb}
                %endif
            %endfor
        %else:
            %if isinstance(field._pt_container, (Struct, Union)):
        scalar |= (${fname}.pack() & 0x${f"{field._pt_mask:X}"}) << ${field._pt_lsb}
            %elif isinstance(field._pt_container, Enum):
        scalar |= (int(${fname}) & 0x${f"{field._pt_mask:X}"}) << ${field._pt_lsb}
            %endif
        %endif
    %endfor
        return scalar

    def unpack(self, scalar, force=False):
        """ Unpack ${obj._pt_name} from a ${int(obj._pt_width)} bit scalar

        Args:
            scalar: The packed scalar value to unpack
            force : Ignore the union check
        """
        # If there is an overarching union, use that to unpack instead
        if self.__pt_union and not force: return self.__pt_union.unpack(scalar)
        # Otherwise, unpack the scalar
    %for field in sorted(obj._pt_values(), key=lambda x: x._pt_lsb):
<%      fname = f"self.__{tc.snake_case(field._pt_name)}" %>\
        %if isinstance(field, Scalar):
        ${fname} = (scalar >> ${field._pt_lsb}) & 0x${f"{field._pt_mask:X}"}
        %elif isinstance(field, Array):
<%
            fmask = int(field._pt_container._pt_mask)
            fwidth = int(field._pt_container._pt_width)
%>\
            %for idx in range(field._pt_count):
<%              lsb = field._pt_lsb + fwidth * idx %>\
                %if isinstance(field._pt_container, (Struct, Union)):
        ${fname}[${idx}].unpack((scalar >> ${lsb}) & 0x${f"{fmask:X}"})
                %elif isinstance(field._pt_container, Enum):
        ${fname}[${idx}] = ${field._pt_container._pt_name}((scalar >> ${lsb}) & 0x${f"{fmask:X}"})
                %endif
            %endfor
        %else:
            %if isinstance(field._pt_container, (Struct, Union)):
        ${fname}.unpack((scalar >> ${field._pt_lsb}) & 0x${f"{field._pt_mask:X}"})
            %elif isinstance(field._pt_container, Enum):
        ${fname} = ${field._pt_container._pt_name}((scalar >> ${field._pt_lsb}) & 0x${f"{field._pt_mask:X}"})
            %endif
        %endif
    %endfor

%endfor ## obj in filter(lambda x: isinstance(x, Struct)), package._pt_values()):
# ==============================================================================
# Unions
# ==============================================================================

%for obj in filter(lambda x: isinstance(x, Union), package._pt_values()):
${blocks.section(obj, delim="#", style="pascal")}
class ${obj._pt_name}:
    %if obj._pt_desc:
<%      desc = obj._pt_desc %>\
    """
        %while desc:
    ${desc[:76]}
<%          desc = desc[76:] %>\
        %endwhile
    """
    %endif

    def __init__(
        self,
        _pt_value=None,
        _pt_parent=None,
    %for field in obj._pt_values():
        %if isinstance(field, Instance) and isinstance(field._pt_container, Enum):
        ${field._pt_name | tc.snake_case}=${field._pt_container._pt_name}.${list(field._pt_keys())[0]},
        %else:
        ${field._pt_name | tc.snake_case}=0,
        %endif
    %endfor
    ):
        # Declare fields
    %for field in obj._pt_values():
        %if isinstance(field, Scalar):
        self.__${field._pt_name} = ${field._pt_name | tc.snake_case}
        %elif isinstance(field._pt_container, (Struct, Union)):
        self.__${field._pt_name | tc.snake_case} = ${field._pt_container._pt_name}(${field._pt_name | tc.snake_case}, _pt_parent=self)
        %elif isinstance(field._pt_container, Enum):
        self.__${field._pt_name | tc.snake_case} = ${field._pt_container._pt_name}(${field._pt_name | tc.snake_case})
        %endif
    %endfor
        # Keep track of parent variables
        self.__pt_parent = _pt_parent
        # If a value was provided, decode it
        if _pt_value is not None:
            self.unpack(_pt_value)

    def _pt_updated(self, child):
        if self.__pt_parent:
            return self.__pt_parent._pt_updated(self)
        self.unpack(child.pack(), exclude=child)

    %for field in obj._pt_values():
    @property
    def ${field._pt_name}(self):
        return self.__${field._pt_name}

    @${field._pt_name}.setter
    def ${field._pt_name}(self, value):
        return self.unpack(value)

    %endfor
    def pack(self):
<%  field = list(obj._pt_values())[0] %>\
    %if isinstance(field, Scalar):
        return self.__${field._pt_name}
    %elif isinstance(field._pt_container, (Struct, Union)):
        return self.__${field._pt_name}.pack()
    %elif isinstance(field._pt_container, Enuma):
        return int(self.__${field._pt_name})
    %endif

    def unpack(self, scalar, exclude=None):
        """ Unpack ${obj._pt_name} from a ${int(obj._pt_width)} bit scalar

        Args:
            scalar : The packed scalar value to unpack
            exclude: Optional field to exclude from update (to avoid recursion)
        """
    %for field in obj._pt_values():
        if self.__${field._pt_name} != exclude:
        %if isinstance(field, Scalar):
            self.__${field._pt_name} = scalar
        %elif isinstance(field._pt_container, (Struct, Union)):
            self.__${field._pt_name}.unpack(scalar)
        %elif isinstance(field._pt_container, Enum):
            self.__${field._pt_name} = ${field._pt_container._pt_name}(scalar)
        %endif
    %endfor

%endfor