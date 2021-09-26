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

#ifndef __${tc.snake_case(name).upper()}_H__
#define __${tc.snake_case(name).upper()}_H__

#include <stdint.h>
#include <string.h>

// =============================================================================
// Constants
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Constant), package._pt_values()):
// ${obj.name.upper()}${tc.opt_desc(obj, " :")}
const ${tc.c_obj_type(obj)} ${tc.snake_case(name).upper()}_${obj.name.upper()} = ${f"0x{obj.value:08X}"};
%endfor ## obj in filter(lambda x: isinstance(x, Constant), package._pt_values())

// =============================================================================
// Enumerations
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Enum), package._pt_values()):
${blocks.section(obj, name=name)}
typedef enum {
<%  prefix = " " %>\
    %for field in obj._pt_values():
    ${prefix} ${tc.snake_case(name).upper()}_${tc.snake_case(obj._pt_name).upper()}_${tc.snake_case(field._pt_name).upper()} = ${field.value}
<%      prefix = "," %>\
    %endfor ## field in obj._pt_values()
} ${name | tc.snake_case}_${obj._pt_name | tc.snake_case}_t;

%endfor ## obj in filter(lambda x: isinstance(x, Enum), package._pt_values())
// =============================================================================
// Data Structures
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Struct), package._pt_values()):
${blocks.section(obj, name=name)}
typedef struct {
    %for field in obj._pt_values():
        %if isinstance(field, Scalar):
    ${tc.c_obj_type(field)} ${field._pt_name};
        %elif type(field._pt_container) in (Enum, Struct):
    ${name | tc.snake_case}_${field._pt_container._pt_name | tc.snake_case}_t ${field._pt_name | tc.snake_case};
        %endif
    %endfor ## field in obj._pt_values()
} ${name | tc.snake_case}_${obj._pt_name | tc.snake_case}_t;

%endfor ## obj in filter(lambda x: isinstance(x, Struct)), package._pt_values()):
// =============================================================================
// Struct Pack/Unpack Routines
// =============================================================================

%for obj in filter(lambda x: isinstance(x, Struct), package._pt_values()):
/** Pack ${obj._pt_name} into a byte array
 *
 * @param obj    the object to pack
 * @param packed pointer to byte array to pack into
 */
void pack_${name | tc.snake_case}_${obj._pt_name | tc.snake_case} (
    ${name | tc.snake_case}_${obj._pt_name | tc.snake_case}_t obj,
    uint8_t * packed
);

/** Unpack ${obj._pt_name} from a byte array
 *
 * @param packed pointer to byte array to unpack
 * @return the unpacked object
 */
${name | tc.snake_case}_${obj._pt_name | tc.snake_case}_t unpack_${name | tc.snake_case}_${obj._pt_name | tc.snake_case} (
    uint8_t * packed
);

%endfor
#endif // __${tc.snake_case(name).upper()}_H__
