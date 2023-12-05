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
<!--
<%include file="header.mako" args="delim=''" />\
-->

<!doctype html>
<html lang="en">
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-F3w7mX95PdgyTmZZMECAngseQB83DfGTowi0iMjiWaeVhAn4FJkqJByhZMI3AhiU" crossorigin="anonymous">

    <title>${name}</title>
</head>
<body>
    <div class="container py-3">

        <h1>${name}</h1>

        <br />
        <hr />
        <br />

        <h2>Constants</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>Constant</th>
                    <th>Value</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
%for obj in filter(lambda x: isinstance(x, Constant), package._pt_values()):
                <tr>
                    <td>${obj.name}</td>
                    <td>${f"0x{obj.value:X}"}</td>
                    <td>${obj.desc}</td>
                </tr>
%endfor ## obj in filter(lambda x: isinstance(x, Constant), package._pt_values())
            </tbody>
        </table>

        <br />
        <hr />
        <br />

        <h2>Enumerations</h2>
%for obj in filter(lambda x: isinstance(x, Enum), package._pt_values()):
        <h3>${obj._pt_name}</h3>
        ${(obj._pt_desc) if obj._pt_desc else ''}
        <table class="table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Value</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
    %for field in obj._pt_values():
                <tr>
                    <td>${field._pt_name}</td>
                    <td>${f"0x{field.value:X}"}</td>
                    <td>${field._pt_desc}</td>
                </tr>
    %endfor ## field in obj._pt_values()
            </tbody>
        </table>
%endfor ## obj in filter(lambda x: isinstance(x, Enum), package._pt_values())

        <br />
        <hr />
        <br />

        <h2>Data Structures</h2>
%for obj in filter(lambda x: isinstance(x, Struct), package._pt_values()):
        <h3>${obj._pt_name}</h3>
        ${(obj._pt_desc) if obj._pt_desc else ''}
        <table class="table">
            <thead>
                <tr>
                    <th>Field</th>
                    <th>Width</th>
                    <th>LSB</th>
                    <th>MSB</th>
                    <th>Type</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
    %for field in obj._pt_values():
                <tr>
                    <td>${field._pt_name}</td>
                    <td>${field._pt_width}</td>
                    <td>${field._pt_lsb}</td>
                    <td>${field._pt_msb}</td>
        %if isinstance(field, Scalar):
                    <td>Scalar</td>
        %elif type(field._pt_container) in (Enum, Struct):
                    <td>${field._pt_container._pt_name}</td>
        %endif
                    <td>${field._pt_desc}</td>
            </tr>
    %endfor ## field in obj._pt_values()
            </tbody>
        </table>
%endfor ## obj in filter(lambda x: isinstance(x, Struct)), package._pt_values())

        <br />
        <hr />
        <br />

        <h2>Unions</h2>
%for obj in filter(lambda x: isinstance(x, Union), package._pt_values()):
        <h3>${obj._pt_name}</h3>
        ${(obj._pt_desc + '. ') if obj._pt_desc else ''}This union is ${obj._pt_width} bits wide.
        <table class="table">
            <thead>
                <tr>
                    <th>Field</th>
                    <th>Type</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
    %for field in obj._pt_values():
                <tr>
                    <td>${field._pt_name}</td>
        %if isinstance(field, Scalar):
                    <td>Scalar (${field._pt_width} bits)</td>
        %elif type(field._pt_container) in (Enum, Struct):
                    <td>${field._pt_container._pt_name}</td>
        %endif
                    <td>${field._pt_desc}</td>
            </tr>
    %endfor ## field in obj._pt_values()
            </tbody>
        </table>
%endfor ## obj in filter(lambda x: isinstance(x, Struct)), package._pt_values())
    </div>
</body>
</html>
