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
<%
import math
max_offset = baseline._pt_max_offset
byte_width = int(math.ceil(math.log2(max_offset + 1)))
%>\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${type(baseline).__name__} Registers</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
          rel="stylesheet"
          integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
          crossorigin="anonymous">
  </head>
  <body>
    <div class="container">
        <h1>${type(baseline).__name__} ${byte_width}</h1>
%for reg in baseline:
        <h2>0x${f"{reg._pt_offset:0{(byte_width+3)//4}X}"}: ${reg._pt_fullname}</h2>
        ${reg.__doc__}
<%
        svg_cfg = SvgConfig()
        svg_cfg.padding = Point(0, 30)
        svg_cfg.per_bit_width = 15
        svg = SvgRender(svg_cfg)
        for f_lsb, f_msb, (name, field) in reg._pt_fields_msb_desc:
            svg.attach(
                SvgField(
                    bit_width=int(field._pt_width),
                    name="" if name == "_padding" else name,
                    msb=int(f_msb),
                    style=[ElementStyle.NORMAL, ElementStyle.HATCHED][name == "_padding"],
                )
            )
%>\
        <br />
        ${svg.render()}
        <br />
        <table class="table">
            <thead>
                <tr>
                    <th scope="col">MSB</th>
                    <th scope="col">LSB</th>
                    <th scope="col">Name</th>
                    <th scope="col">Behaviour</th>
                    <th scope="col">Width</th>
                    <th scope="col">Value</th>
                    <th scope="col">Description</th>
                </tr>
            </thead>
            <tbody>
    %for f_lsb, f_msb, (name, field) in reg._pt_fields_msb_desc:
                <tr>
                    <td>${f_msb}</td>
                    <td>${f_lsb}</td>
                    <td>${name}</td>
                    <td>${reg._PT_BEHAVIOUR.name}</td>
                    <td>${field._pt_width}</td>
                    <td>0x${f"{int(field):X}"}</td>
                    <td>${field.__doc__}</td>
                </tr>
    %endfor ## field in reg._pt_fields_msb_desc
            </tbody>
        </table>
%endfor ## reg in baseline
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
            crossorigin="anonymous"></script>
  </body>
</html>
