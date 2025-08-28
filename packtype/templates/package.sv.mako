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
package ${baseline._pt_name() | filters.package};

// =============================================================================
// Imports
// =============================================================================

%for foreign in baseline._pt_foreign():
    %if foreign._PT_ATTACHED_TO:
<%      refers_to = foreign._PT_ATTACHED_TO._pt_lookup(foreign) %>\
import ${foreign._PT_ATTACHED_TO._pt_name() | filters.package}::${refers_to | filters.type};
    %else:
import ${foreign._PT_ATTACHED_TO._pt_name() | filters.package}::${foreign._pt_name() | filters.type};
    %endif
%endfor ## foreign in baseline._pt_foreign()

// =============================================================================
// Constants
// =============================================================================

%for name, obj in baseline._pt_constants:
// ${name.upper()}
    %if utils.get_width(obj) > 0:
localparam bit [${utils.get_width(obj)-1}:0] ${name | filters.constant} = ${utils.get_width(obj)}'h${f"{obj.value:0{(utils.get_width(obj)+3)//4}X}"};
    %elif obj.value >= (1 << 32):
localparam ${name | filters.constant} = 64'h${f"{obj.value:08X}"};
    %else:
localparam ${name | filters.constant} = 'h${f"{obj.value:08X}"};
    %endif
%endfor

// =============================================================================
// Typedefs
// =============================================================================

%for name, objcls in baseline._pt_scalars:
<%  obj = objcls() %>\
// ${name}
typedef logic [${utils.get_width(obj)-1}:0] ${name | filters.type};
%endfor
%for name, obj in baseline._pt_aliases:
// ${name}
typedef ${obj._PT_ALIAS._pt_name() | filters.type} ${name | filters.type};
%endfor

// =============================================================================
// Enumerations
// =============================================================================

%for name, objcls in baseline._pt_enums:
<%  obj = objcls() %>\
// ${name}
typedef enum logic [${utils.get_width(obj)-1}:0] {
<%  sep = " " %>\
    %for field, fname in obj._PT_LKP_INST.items():
<%
        prefix = tc.snake_case(obj._PT_PREFIX).upper()
        prefix += ["", "_"][len(prefix) > 0]
%>\
    ${sep} ${prefix}${tc.snake_case(fname).upper()} = ${utils.get_width(obj)}'d${field.value}
<%      sep = "," %>\
    %endfor
} ${name | filters.type};

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
        next_pos = utils.get_width(obj) - 1
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
            %if isinstance(field, ScalarType):
                %if field._PT_ATTACHED_TO:
<%                  refers_to = field._pt_name() %>\
    ${refers_to | filters.type}${array_sfx} ${fname | tc.snake_case};
                %else:
<%                  sign_sfx = " signed" if field._pt_signed else "" %>\
    logic${sign_sfx}${array_sfx}${f" [{utils.get_width(field)}:0]" if utils.get_width(field) > 1 else ""} ${fname | tc.snake_case};
                %endif
            %elif isinstance(field, Alias | Enum | Struct | Union):
    ${field._pt_name() | filters.type}${array_sfx} ${fname | tc.snake_case};
            %endif
<%          next_pos = (flsb - 1) %>\
        %endfor
        %if msb_pack and next_pos >= 0:
<%          pad_width = next_pos + 1 %>\
    logic${f" [{pad_width-1}:0]" if pad_width > 1 else ""} _padding_${pad_idx};
        %endif
} ${obj._pt_name() | filters.type};
    %elif isinstance(obj, Union):
typedef union packed {
        %for field, fname in obj._pt_fields.items():
<%
            array_sfx = f" [{len(field)-1}:0]" if isinstance(field, PackedArray) else ""
            field = field[0] if isinstance(field, PackedArray) else field
%>\
            %if isinstance(field, ScalarType):
                %if field._PT_ATTACHED_TO:
<%                  refers_to = field._pt_name() %>\
    ${refers_to | filters.type} ${fname | tc.snake_case};
                %else:
<%                  sign_sfx = " signed" if field._pt_signed else "" %>\
    logic${sign_sfx}${f" [{utils.get_width(field)}:0]" if utils.get_width(field) > 1 else ""} ${fname | tc.snake_case};
                %endif
            %elif isinstance(field, Enum | Struct | Alias | Union):
    ${field._pt_name() | filters.type}${array_sfx} ${fname | tc.snake_case};
            %endif
        %endfor
} ${obj._pt_name() | filters.type};
    %endif

%endfor

endpackage : ${baseline._pt_name() | filters.package}

/* verilator lint_on UNUSEDPARAM */
