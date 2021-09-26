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
<%include file="header.mako" args="delim='//'" />\
<%namespace name="blocks" file="blocks.mako" />\

#include "${name | tc.snake_case}.hpp"

%for obj in filter(lambda x: isinstance(x, Struct), package._pt_values()):
void ${name}::pack_${obj._pt_name | tc.snake_case} (
    ${name}::${obj._pt_name | tc.snake_case}_t obj,
    uint8_t * packed
) {
    // Clear the structure
    memset((void *)packed, 0, ${(obj._pt_width + 7) // 8});
    // Pack any referenced structs
    %for field in filter(lambda x: isinstance(x, Instance) and isinstance(x._pt_container, Struct), obj._pt_values()):
    // - ${field._pt_name | tc.snake_case} (${field._pt_width} bits)
    uint8_t packed_${field._pt_name | tc.snake_case}[${(field._pt_width + 7) // 8}];
    pack_${field._pt_container._pt_name | tc.snake_case}(obj.${field._pt_name}, packed_${field._pt_name | tc.snake_case});
<%
        field_lsb  = 0
        offset_lsb = field._pt_lsb
%>\
        %while field_lsb < field._pt_width:
<%
            step  = min(
                (((offset_lsb + 8) // 8) * 8) - offset_lsb,
                (((field_lsb  + 8) // 8) * 8) - field_lsb,
                field._pt_width - field_lsb,
            )
            mask  = ((1 << step) - 1) << (field_lsb % 8)
            shift = (offset_lsb % 8) - (field_lsb % 8)
%>\
    packed[${offset_lsb // 8}] |= (packed_${field._pt_name | tc.snake_case}[${field_lsb // 8}] & ${f"0x{mask:02X}"}) ${"<<" if shift > 0 else ">>"} ${abs(shift)};
<%
            field_lsb  += step
            offset_lsb += step
%>\
        %endwhile
    %endfor
    // Pack scalar and enumerated fields
    %for field in filter(lambda x: isinstance(x, Scalar) or (isinstance(x, Instance) and isinstance(x._pt_container, Enum)), obj._pt_values()):
    // - ${field._pt_name | tc.snake_case} (${field._pt_width} bits)
<%
        field_lsb  = 0
        offset_lsb = field._pt_lsb
%>\
        %while field_lsb < field._pt_width:
<%
            step  = min(
                (((offset_lsb + 8) // 8) * 8) - offset_lsb,
                field._pt_width - field_lsb,
            )
            shift = (offset_lsb % 8) - field_lsb
            mask  = ((1 << step) - 1) << (offset_lsb % 8)
%>\
    packed[${offset_lsb // 8}] |= (obj.${field._pt_name} ${"<<" if shift > 0 else ">>"} ${abs(shift)}) & ${f"0x{mask:02X}"};
<%
            field_lsb  += step
            offset_lsb += step
%>\
        %endwhile
    %endfor
}

${name}::${obj._pt_name | tc.snake_case}_t ${name}::unpack_${obj._pt_name | tc.snake_case} (
    uint8_t * packed
) {
    ${obj._pt_name | tc.snake_case}_t obj;
    // Unpack any referenced structures
    %for field in filter(lambda x: isinstance(x, Instance) and isinstance(x._pt_container, Struct), obj._pt_values()):
    // - ${field._pt_name | tc.snake_case} (${field._pt_width} bits)
    uint8_t packed_${field._pt_name | tc.snake_case}[${(field._pt_width + 7) // 8}];
    memset((void *)packed_${field._pt_name | tc.snake_case}, 0, ${(field._pt_width + 7) // 8});
<%
        field_lsb  = 0
        offset_lsb = field._pt_lsb
%>\
        %while field_lsb < field._pt_width:
<%
            step  = min(
                (((offset_lsb + 8) // 8) * 8) - offset_lsb,
                (((field_lsb  + 8) // 8) * 8) - field_lsb,
                field._pt_width - field_lsb,
            )
            mask  = ((1 << step) - 1) << (field_lsb % 8)
            shift = (offset_lsb % 8) - (field_lsb % 8)
%>\
    packed_${field._pt_name | tc.snake_case}[${field_lsb // 8}] |= (packed[${offset_lsb // 8}] ${"<<" if shift < 0 else ">>"} ${abs(shift)}) & ${f"0x{mask:02X}"};
<%
            field_lsb  += step
            offset_lsb += step
%>\
        %endwhile
    obj.${field._pt_name | tc.snake_case} = unpack_${field._pt_container._pt_name | tc.snake_case}(packed_${field._pt_name | tc.snake_case});
    %endfor
    // Unpack any scalar or enumerated fields
    %for field in filter(lambda x: isinstance(x, Scalar) or (isinstance(x, Instance) and isinstance(x._pt_container, Enum)), obj._pt_values()):
    // - ${field._pt_name | tc.snake_case} (${field._pt_width} bits)
        %if isinstance(field, Scalar):
    obj.${field._pt_name | tc.snake_case} = 0;
        %else:
    ${tc.c_obj_type(field)} value_${field._pt_name | tc.snake_case} = 0;
        %endif
<%
        field_lsb  = 0
        offset_lsb = field._pt_lsb
%>\
        %while field_lsb < field._pt_width:
<%
            step  = min(
                (((offset_lsb + 8) // 8) * 8) - offset_lsb,
                field._pt_width - field_lsb,
            )
            shift = (offset_lsb % 8) - field_lsb
            mask  = ((1 << step) - 1) << (offset_lsb % 8)
%>\
            %if isinstance(field, Scalar):
    obj.${field._pt_name | tc.snake_case} \
            %else:
    value_${field._pt_name | tc.snake_case} \
            %endif
|= (packed[${offset_lsb // 8}] & ${f"0x{mask:02X}"}) ${"<<" if shift < 0 else ">>"} ${abs(shift)};
<%
            field_lsb  += step
            offset_lsb += step
%>\
        %endwhile
        %if not isinstance(field, Scalar):
    obj.${field._pt_name} = (${field._pt_container._pt_name | tc.snake_case}_t)value_${field._pt_name | tc.snake_case};
        %endif
    %endfor
    return obj;
}

%endfor