<%doc>
Copyright 2023, Peter Birch, mailto:peter@intuity.io

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
import math
max_offset = baseline._pt_max_offset
byte_width = int(math.ceil(math.log2(max_offset + 1)))
base_types = {x for x in baseline._pt_references() if x._PT_BASE is Register}

def width(obj):
    return int(obj._pt_width) - 1
%>\

/* verilator lint_off UNUSEDPARAM */

package ${type(baseline).__name__ | tc.snake_case}_pkg;

// =============================================================================
// Foreign
// =============================================================================

%for foreign in baseline._pt_foreign():
    %if foreign._PT_ATTACHED_TO:
<%      refers_to = foreign._PT_ATTACHED_TO._pt_lookup(foreign) %>\
import ${foreign._PT_ATTACHED_TO._pt_name() | tc.snake_case}::${refers_to | tc.snake_case}_t;
    %else:
import ${foreign._PT_ATTACHED_TO._pt_name() | tc.snake_case}::${foreign._pt_name() | tc.snake_case}_t;
    %endif
%endfor ## foreign in baseline._pt_foreign()

// =============================================================================
// Offsets
// =============================================================================

typedef enum logic [${byte_width-1}:0] {
%for idx, reg in enumerate(baseline):
    ${"," if idx else " "} ${reg._pt_fullname.upper() | tc.underscore}_OFFSET = 'h${f"{reg._pt_offset:X}"}
%endfor ## reg in baseline
} offset_t;

// =============================================================================
// Structures
// =============================================================================

%for base in sorted(base_types, key=lambda x: x.__name__):
typedef struct packed {
    %for f_lsb, f_msb, (name, field) in base()._pt_fields_msb_desc:
        %if isinstance(field, NumericPrimitive):
            %if field._pt_width > 1:
    logic [${field._pt_width-1}:0] ${name | tc.snake_case};
            %else:
    logic ${name | tc.snake_case};
            %endif
        %elif field._PT_BASE in (Enum, Struct, Union):
    ${field._pt_name() | tc.snake_case}_t ${name | tc.snake_case};
        %endif
    %endfor ## f_lsb, f_msb, (name, field) in base()._pt_fields_msb_desc
} ${base.__name__ | tc.snake_case}_t;

%endfor ## base in base_types
endpackage : ${type(baseline).__name__ | tc.snake_case}_pkg

/* verilator lint_on UNUSEDPARAM */
