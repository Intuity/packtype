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
    return int(obj._pt_width) - 1
%>\

/* verilator lint_off UNUSEDPARAM */

package ${name | tc.snake_case};

// =============================================================================
// Imports
// =============================================================================

%for foreign in package._pt_foreign():
import ${foreign._pt_parent._pt_name | tc.snake_case}::${foreign._pt_name | tc.snake_case}_t;
%endfor ## foreign in package._pt_foreign()

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
${blocks.section(obj)}
    %if obj._pt_alias is None:
typedef logic [${width(obj)}:0] ${obj._pt_name | tc.snake_case}_t;
    %else:
typedef ${obj._pt_alias._pt_name | tc.snake_case}_t ${obj._pt_name | tc.snake_case}_t;
    %endif
%endfor

// =============================================================================
// Enumerations
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Enum), package._pt_values()):
${blocks.section(obj)}
typedef enum logic [${width(obj)}:0] {
<%  sep = " " %>\
    %for field in obj._pt_values():
<%
        prefix = tc.snake_case(obj._pt_prefix).upper()
        prefix += ["", "_"][len(prefix) > 0]
%>\
    ${sep} ${prefix}${tc.snake_case(field._pt_name).upper()} = 'd${field.value}
<%      sep = "," %>\
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
<%              pad_width = (next_pos - field._pt_msb) %>\
    logic${f" [{pad_width-1}:0]" if pad_width > 1 else ""} _padding_${pad_idx};
<%              pad_idx += 1 %>\
            %endif
            %if isinstance(field, Scalar):
<%              sign_sfx = " signed" if field._pt_signed else "" %>\
    logic${sign_sfx}${f" [{width(field)}:0]" if field._pt_width > 1 else ""} ${field._pt_name};
            %elif type(field._pt_container) in (Enum, Struct, Typedef, Union):
<%              array_sfx = f" [{field._pt_count-1}:0]" if isinstance(field, Array) else "" %>\
    ${field._pt_container._pt_name | tc.snake_case}_t${array_sfx} ${field._pt_name | tc.snake_case};
            %endif
<%          next_pos = (field._pt_lsb - 1) %>\
        %endfor
        %if msb_pack and next_pos >= 0:
<%          pad_width = next_pos + 1 %>\
    logic${f" [{pad_width-1}:0]" if pad_width > 1 else ""} _padding_${pad_idx};
        %endif
    %elif isinstance(obj, Union):
        %for field in obj._pt_values():
            %if isinstance(field, Scalar):
<%              sign_sfx = " signed" if field._pt_signed else "" %>\
    logic${sign_sfx}${f" [{width(field)}:0]" if field._pt_width > 1 else ""} ${field._pt_name};
            %elif type(field._pt_container) in (Enum, Struct, Typedef, Union):
<%              array_sfx = f" [{field._pt_count-1}:0]" if isinstance(field, Array) else "" %>\
    ${field._pt_container._pt_name | tc.snake_case}_t${array_sfx} ${field._pt_name | tc.snake_case};
            %endif
        %endfor
    %endif
} ${obj._pt_name | tc.snake_case}_t;

%endfor

endpackage : ${name | tc.snake_case}

/* verilator lint_on UNUSEDPARAM */