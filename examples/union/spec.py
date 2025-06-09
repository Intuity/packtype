# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

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
