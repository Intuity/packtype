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

<%def name="section(obj, name=None, delim='//', indent=0, style='snake')">\
<%
    indent   = (' ' * indent)
    obj_name = {
        "pascal": obj._pt_name,
        "snake" : tc.snake_case(obj._pt_name) + "_t",
    }[style]
    if isinstance(name, str): obj_name = tc.snake_case(name) + "_" + obj_name
%>\
${indent}${delim} ${type(obj).__name__}: ${obj_name} (${obj._pt_width} bits)
%if obj._pt_desc:
<%  full_desc = obj._pt_desc %>\
    %while full_desc:
${indent}${delim} ${full_desc[:76]}
<%      full_desc = full_desc[76:] %>\
    %endwhile
%endif
${indent}${delim}\
</%def>\
