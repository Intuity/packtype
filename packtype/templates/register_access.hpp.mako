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
cls_name = type(baseline).__name__
base_types = {x for x in baseline._pt_references() if x._PT_BASE is Register}
%>\

#ifndef ${cls_name | tc.shouty_snake_case}_ACCESS_HPP
#define ${cls_name | tc.shouty_snake_case}_ACCESS_HPP

#include <cstdint>

namespace packtype {

class ${cls_name}Access {
public:

    // =========================================================================
    // Register Offsets
    // =========================================================================

    enum Offset {
%for idx, reg in enumerate(baseline):
        ${"," if idx else " "} ${reg._pt_fullname.upper() | tc.underscore}_OFFSET = 0x${f"{reg._pt_offset:X}"}
%endfor ## reg in baseline
    };

    // =========================================================================
    // Register Formats
    // =========================================================================

%for base in sorted(base_types, key=lambda x: x.__name__):
    struct ${base.__name__ | tc.camel_case} {
    %for _, _, (name, _) in base()._pt_fields_msb_desc:
        std::uint64_t ${name | tc.snake_case};
    %endfor ## _, _, (name, _) in base()._pt_fields_msb_desc
    };

%endfor ## base in base_types
    // =========================================================================
    // Pack/Unpack Methods
    // =========================================================================

%for base in sorted(base_types, key=lambda x: x.__name__):
    static ${base.__name__ | tc.camel_case} unpack_${base.__name__ | tc.snake_case} (std::uint64_t value)
    {
        ${base.__name__ | tc.camel_case} unpacked;
    %for lsb, _, (name, field) in base()._pt_fields_msb_desc:
        unpacked.${name | tc.snake_case} = ((value >> ${lsb}) & 0x${f"{(1 << field._pt_width) - 1:X}"});
    %endfor ## lsb, _, (name, field) in base()._pt_fields_msb_desc
        return unpacked;
    }

    static std::uint64_t pack_${base.__name__ | tc.snake_case} (${base.__name__ | tc.camel_case} data)
    {
        std::uint64_t value = 0;
    %for lsb, _, (name, field) in base()._pt_fields_msb_desc:
        value |= (data.${name | tc.snake_case} & 0x${f"{(1 << field._pt_width) - 1:X}"}) << ${lsb};
    %endfor ## lsb, _, (name, field) in base()._pt_fields_msb_desc
        return value;
    }

%endfor ## base in base_types
}; // ${cls_name}Access

} // packtype

#endif // ${cls_name | tc.shouty_snake_case}_ACCESS_HPP
