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

/* verilator lint_off UNUSEDPARAM */

package ${baseline._pt_name() | tc.snake_case};

// =============================================================================
// Imports
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
// Constants
// =============================================================================

%for name, obj in baseline._pt_constants:
// ${name.upper()}
    %if utils.width(obj) > 0:
localparam bit [${utils.width(obj)-1}:0] ${name | tc.shouty_snake_case} = ${utils.width(obj)}'h${f"{obj.value:0{(utils.width(obj)+3)//4}X}"};
    %elif obj.value >= (1 << 32):
localparam ${name | tc.shouty_snake_case} = 64'h${f"{obj.value:08X}"};
    %else:
localparam ${name | tc.shouty_snake_case} = 'h${f"{obj.value:08X}"};
    %endif
%endfor

// =============================================================================
// Typedefs
// =============================================================================

%for name, objcls in baseline._pt_scalars:
<%  obj = objcls() %>\
// ${name}
typedef logic [${utils.width(obj)-1}:0] ${name | tc.snake_case}_t;
%endfor
%for name, obj in baseline._pt_aliases:
// ${name}
typedef ${obj._PT_ALIAS._pt_name() | tc.snake_case}_t ${name | tc.snake_case}_t;
%endfor

// =============================================================================
// Enumerations
// =============================================================================

%for name, objcls in baseline._pt_enums:
<%  obj = objcls() %>\
// ${name}
typedef enum logic [${utils.width(obj)-1}:0] {
<%  sep = " " %>\
    %for field, fname in obj._PT_LKP_INST.items():
<%
        prefix = tc.snake_case(obj._PT_PREFIX).upper()
        prefix += ["", "_"][len(prefix) > 0]
%>\
    ${sep} ${prefix}${tc.snake_case(fname).upper()} = ${utils.width(obj)}'d${field.value}
<%      sep = "," %>\
    %endfor
} ${name | tc.snake_case}_t;

%endfor
// =============================================================================
// Structs and Unions
// =============================================================================

%for name, objcls in baseline._pt_structs_and_unions:
<%  obj = objcls() %>\
// ${name}
    %if isinstance(obj, Struct):
typedef struct packed {
<%
        msb_pack = (obj._PT_PACKING == Packing.FROM_MSB)
        next_pos = utils.width(obj) - 1
        pad_idx  = 0
%>\
        %for flsb, fmsb, (fname, field) in obj._pt_fields_msb_desc:
            %if fmsb != next_pos:
<%              pad_width = (next_pos - fmsb) %>\
    logic${f" [{pad_width-1}:0]" if pad_width > 1 else ""} _padding_${pad_idx};
<%              pad_idx += 1 %>\
            %endif
<%
            array_sfx = f" [{len(field)-1}:0]" if isinstance(field, PackedArray) else ""
            field = field[0] if isinstance(field, PackedArray) else field
%>\
            %if isinstance(field, Scalar):
                %if field._PT_ATTACHED_TO:
<%                  refers_to = field._PT_ATTACHED_TO._pt_lookup(type(field)) %>\
    ${refers_to | tc.snake_case}_t${array_sfx} ${fname | tc.snake_case};
                %else:
<%                  sign_sfx = " signed" if field._pt_signed else "" %>\
    logic${sign_sfx}${array_sfx}${f" [{utils.width(field)}:0]" if utils.width(field) > 1 else ""} ${fname | tc.snake_case};
                %endif
            %elif isinstance(field, Alias | Enum | Struct | Union):
    ${field._pt_name() | tc.snake_case}_t${array_sfx} ${fname | tc.snake_case};
            %endif
<%          next_pos = (flsb - 1) %>\
        %endfor
        %if msb_pack and next_pos >= 0:
<%          pad_width = next_pos + 1 %>\
    logic${f" [{pad_width-1}:0]" if pad_width > 1 else ""} _padding_${pad_idx};
        %endif
} ${obj._pt_name() | tc.snake_case}_t;
    %elif isinstance(obj, Union):
typedef union packed {
        %for field, fname in obj._pt_fields.items():
<%
            array_sfx = f" [{len(field)-1}:0]" if isinstance(field, PackedArray) else ""
            field = field[0] if isinstance(field, PackedArray) else field
%>\
            %if isinstance(field, Scalar):
                %if field._PT_ATTACHED_TO:
<%                  refers_to = field._PT_ATTACHED_TO._pt_lookup(type(field)) %>\
    ${refers_to | tc.snake_case}_t ${fname | tc.snake_case};
                %else:
<%                  sign_sfx = " signed" if field._pt_signed else "" %>\
    logic${sign_sfx}${f" [{utils.width(field)}:0]" if utils.width(field) > 1 else ""} ${fname | tc.snake_case};
                %endif
            %elif isinstance(field, Enum | Struct | Alias | Union):
    ${field._pt_name() | tc.snake_case}_t${array_sfx} ${fname | tc.snake_case};
            %endif
        %endfor
} ${obj._pt_name() | tc.snake_case}_t;
    %endif

%endfor

endpackage : ${baseline._pt_name() | tc.snake_case}

/* verilator lint_on UNUSEDPARAM */
