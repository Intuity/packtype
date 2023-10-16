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
<%
def width(obj):
    if isinstance(obj._pt_width, Constant):
        return f"{obj._pt_width.name}-1"
    else:
        return obj._pt_width - 1
%>\

/* verilator lint_off UNUSEDPARAM */

package ${name};

// =============================================================================
// Constants
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Constant), package._pt_values()):
// ${obj.name.upper()}${tc.opt_desc(obj, " :")}
localparam ${obj.name.upper()} = 'h${f"{obj.value:08X}"};
%endfor

// =============================================================================
// Typedefs
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Typedef), package._pt_values()):
// ${obj._pt_name.upper()}${tc.opt_desc(obj, " :")}
typedef logic [${width(obj)}:0] ${obj._pt_name}_t;
%endfor

// =============================================================================
// Enumerations
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Enum), package._pt_values()):
${blocks.section(obj)}
typedef enum logic [${width(obj)}:0] {
<%  prefix = " " %>\
    %for field in obj._pt_values():
    ${prefix} ${tc.snake_case(obj._pt_prefix).upper()}_${tc.snake_case(field._pt_name).upper()} = 'd${field.value}
<%      prefix = "," %>\
    %endfor
} ${obj._pt_name | tc.snake_case}_t;

%endfor
// =============================================================================
// Structs and Unions
// =============================================================================

%for obj in filter(lambda x: isinstance(x, (Struct, Union)), package._pt_values()):
${blocks.section(obj)}
typedef ${type(obj).__name__.lower()} packed {
    %if isinstance(obj, Struct):
<%
        msb_pack = (obj._pt_pack == "FROM_MSB")
        next_pos = obj._pt_width - 1
        pad_idx  = 0
        ordered  = reversed(sorted(obj._pt_values(), key=lambda x: x._pt_lsb))
%>\
        %for field in ordered:
            %if field._pt_msb != next_pos:
<%              width = (next_pos - field._pt_msb) %>\
    logic${f" [{width-1}:0]" if width > 1 else ""} _padding_${pad_idx};
<%              pad_idx += 1 %>\
            %endif
            %if isinstance(field, Scalar):
    logic${f" [{width(field)}:0]" if field._pt_width > 1 else ""} ${field._pt_name};
            %elif type(field._pt_container) in (Enum, Struct, Typedef, Union):
<%              array_sfx = f" [{field._pt_count-1}:0]" if isinstance(field, Array) else "" %>\
    ${field._pt_container._pt_name | tc.snake_case}_t${array_sfx} ${field._pt_name | tc.snake_case};
            %endif
<%          next_pos = (field._pt_lsb - 1) %>\
        %endfor
        %if msb_pack and next_pos >= 0:
<%          width = next_pos + 1 %>\
    logic${f" [{width-1}:0]" if width > 1 else ""} _padding_${pad_idx};
        %endif
    %elif isinstance(obj, Union):
        %for field in obj._pt_values():
            %if isinstance(field, Scalar):
    logic${f" [{field._pt_width-1}:0]" if field._pt_width > 1 else ""} ${field._pt_name};
            %elif type(field._pt_container) in (Enum, Struct, Typedef, Union):
<%              array_sfx = f" [{field._pt_count-1}:0]" if isinstance(field, Array) else "" %>\
    ${field._pt_container._pt_name | tc.snake_case}_t${array_sfx} ${field._pt_name | tc.snake_case};
            %endif
        %endfor
    %endif
} ${obj._pt_name | tc.snake_case}_t;

%endfor

endpackage : ${name}

/* verilator lint_on UNUSEDPARAM */
