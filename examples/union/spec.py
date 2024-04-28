# Copyright 2024, Peter Birch, mailto:peter@intuity.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import packtype
from packtype import Constant, Scalar


@packtype.package()
class Encodings:
    pass


@Encodings.enum()
class Operation:
    ADD: Constant
    SUB: Constant
    MUL: Constant
    DIV: Constant


@Encodings.struct(width=32)
class Add:
    op: Operation
    tgt: Scalar[5]
    src_a: Scalar[5]
    src_b: Scalar[5]


@Encodings.struct(width=32)
class AddImm:
    op: Operation
    tgt: Scalar[5]
    src: Scalar[5]
    imm: Scalar[20]


@Encodings.struct(width=32)
class Sub:
    op: Operation
    tgt: Scalar[5]
    src_a: Scalar[5]
    src_b: Scalar[5]


@Encodings.union()
class Instruction:
    raw: Scalar[32]
    add: Add
    add_imm: Add
