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

package ${name};

    // =========================================================================
    // Constants
    // =========================================================================

%for obj in filter(lambda x: isinstance(x, Constant), package._pt_values()):
    // ${obj.name.upper()}${tc.opt_desc(obj, " :")}
    localparam ${obj.name.upper()} = 'h${f"{obj.value:08X}"};
%endfor ## obj in filter(lambda x: isinstance(x, Constant), package._pt_values())

    // =========================================================================
    // Enumerations
    // =========================================================================

%for obj in filter(lambda x: isinstance(x, Enum), package._pt_values()):
${blocks.section(obj, indent=4)}
    typedef enum logic [${obj._pt_width-1}:0] {
<%  prefix = " " %>\
    %for field in obj._pt_values():
        ${prefix} ${tc.snake_case(obj._pt_name).upper()}_${tc.snake_case(field._pt_name).upper()} = 'd${field.value}
<%      prefix = "," %>\
    %endfor ## field in obj._pt_values()
    } ${obj._pt_name | tc.snake_case}_t;

%endfor ## obj in filter(lambda x: isinstance(x, Enum), package._pt_values())
    // =========================================================================
    // Data Structures
    // =========================================================================

%for obj in filter(lambda x: isinstance(x, Struct), package._pt_values()):
${blocks.section(obj, indent=4)}
    typedef struct packed {
<%  lsb, pad = 0, 0 %>\
    %for field in sorted(obj._pt_values(), key=lambda x: x._pt_lsb):
        %if field._pt_lsb != lsb:
<%          width = field._pt_lsb-lsb %>\
        logic${f" [{width-1}:0]" if width > 1 else ""} _padding_${pad};
<%          pad += 1 %>\
        %endif
        %if isinstance(field, Scalar):
        logic${f" [{field._pt_width-1}:0]" if field._pt_width > 1 else ""} ${field._pt_name};
        %elif type(field._pt_container) in (Enum, Struct):
        ${field._pt_container._pt_name | tc.snake_case}_t ${field._pt_name | tc.snake_case};
        %endif
<%      lsb = field._pt_lsb + field._pt_width %>\
    %endfor ## field in obj._pt_values()
    %if obj._pt_width != lsb:
<%      width = obj._pt_width-lsb %>\
        logic${f" [{width-1}:0]" if width > 1 else ""} _padding_${pad};
    %endif
    } ${obj._pt_name | tc.snake_case}_t;

%endfor
    // =========================================================================
    // Unions
    // =========================================================================

%for obj in filter(lambda x: isinstance(x, Union), package._pt_values()):
${blocks.section(obj, indent=4)}
    typedef union packed {
    %for field in obj._pt_values():
        %if isinstance(field, Scalar):
        logic${f" [{field._pt_width-1}:0]" if field._pt_width > 1 else ""} ${field._pt_name};
        %elif type(field._pt_container) in (Enum, Struct):
        ${field._pt_container._pt_name | tc.snake_case}_t ${field._pt_name | tc.snake_case};
        %endif
    %endfor ## field in obj._pt_values()
    } ${obj._pt_name | tc.snake_case}_t;

%endfor
endpackage : ${name}