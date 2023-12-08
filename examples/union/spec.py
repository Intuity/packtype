# Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk
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

from packtype import scalar
import packtype
from packtype import Constant, Scalar


@packtype.package()
class Encodings:
    pass


@packtype.enum(package=Encodings)
class Operation:
    ADD: Constant("Add two numbers")
    SUB: Constant("Subtract two numbers")
    MUL: Constant("Multiply two numbers")
    DIV: Constant("Divide two numbers")


@packtype.struct(width=32, package=Encodings)
class Add:
    op: Operation(desc="Operation to perform")
    tgt: Scalar(width=5, desc="Target register")
    src_a: Scalar(width=5, desc="Input register A")
    src_b: Scalar(width=5, desc="Input register B")


@packtype.struct(width=32, package=Encodings)
class AddImm:
    op: Operation(desc="Operation to perform")
    tgt: Scalar(width=5, desc="Target register")
    src: Scalar(width=5, desc="Input register A")
    imm: Scalar(width=20, desc="Immediate value")


@packtype.struct(width=32, package=Encodings)
class Sub:
    op: Operation(desc="Operation to perform")
    tgt: Scalar(width=5, desc="Target register")
    src_a: Scalar(width=5, desc="Input register A")
    src_b: Scalar(width=5, desc="Input register B")


@packtype.union(package=Encodings)
class Instruction:
    raw: Scalar(width=32, desc="Raw instruction value")
    add: Add(desc="Add instruction")
    add_imm: Add(desc="Add immediate instruction")
