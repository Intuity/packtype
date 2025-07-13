# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math

import packtype
from packtype import Constant, Scalar


@packtype.package()
class RvUnprivPkg:
    """RISC-V Unprivileged ISA definitions"""

    # === Constants ===

    C_INSTR_W: Constant = 16
    """ Compressed instruction width """
    IMM5_W: Constant = 5
    """ Width of 5-bit immediate field """
    IMM7_W: Constant = 7
    """ Width of 7-bit immediate field """
    IMM12_W: Constant = 12
    """ Width of 12-bit immediate field """
    IMM20_W: Constant = 20
    """ Width of 20-bit immediate field """
    INSTR_W: Constant = 32
    """ Complete instruction width """
    F3_W: Constant = 3
    """ Width of funct3 specifier """
    F7_W: Constant = 7
    """ Width of funct7 specifier """
    OPCODE_W: Constant = 7
    """ Width of opcode specifier """
    QUAD_W: Constant = 2
    """ Width of Quad specifier """
    REGSEL_W: Constant = 5
    """ Width of register selector fields """
    XLEN: Constant = 64
    """ Register width definition """
    SHAMT_W: Constant = math.ceil(math.log2(XLEN))
    """ Shift amount width (based on XLEN) """

    # === Simple Typedefs ===

    Regsel: Scalar[REGSEL_W]
    """ Register selector """
    Shamt: Scalar[SHAMT_W]
    """ Shift amount """


# ==============================================================================
# Opcode Enumeration
# ==============================================================================


@RvUnprivPkg.enum(width=RvUnprivPkg.OPCODE_W)
class Opcode:
    LUI: Constant = 0b0110111
    """ Load upper immediate """
    AUIPC: Constant = 0b0010111
    """ Add unsigned immediate to PC """
    JAL: Constant = 0b1101111
    """ Jump-and-link using immediate offset """
    JALR: Constant = 0b1100111
    """ Jump-and-link using address from register """
    BRANCH: Constant = 0b1100011
    """ Conditional relative branch """
    LOAD: Constant = 0b0000011
    """ Signed/unsigned load operations for doubleword, word, halfword, byte """
    STORE: Constant = 0b0100011
    """ Store operations for doubleword, word, halfword, byte """
    ALU_I: Constant = 0b0010011
    """ Register-immediate arithmetic """
    ALU_R: Constant = 0b0110011
    """ Register-register aritmethic """
    FENCE: Constant = 0b0001111
    """ Fence/control type operations """
    ECALL: Constant = 0b1110011
    """ System calls """


@RvUnprivPkg.enum(width=RvUnprivPkg.QUAD_W)
class Quad:
    Q0: Constant = 0b00
    Q1: Constant = 0b01
    Q2: Constant = 0b10
    Q3: Constant = 0b11


# ==============================================================================
# Funct3
# ==============================================================================


@RvUnprivPkg.enum(width=RvUnprivPkg.F3_W)
class F3Branch:
    """Funct3 encodings of branch conditions"""

    EQ: Constant = 0b000
    NE: Constant = 0b001
    LT: Constant = 0b100
    GE: Constant = 0b101
    LTU: Constant = 0b110
    GEU: Constant = 0b111


@RvUnprivPkg.enum(width=RvUnprivPkg.F3_W)
class F3Atom:
    """Funct3 encodings of load/store atom size"""

    B: Constant = 0b000
    """ Byte """
    H: Constant = 0b001
    """ Half-word (two bytes) """
    W: Constant = 0b010
    """ Word (four bytes) """
    D: Constant = 0b011
    """ Doubleword (eight bytes) """
    BU: Constant = 0b100
    """ Byte unsigned """
    HU: Constant = 0b101
    """ Half-word (two bytes) unsigned """
    WU: Constant = 0b110
    """ Word (four bytes) unsigned """


@RvUnprivPkg.enum(width=RvUnprivPkg.F3_W)
class F3Arith:
    """Funct3 encodings of arithmetic/logical operations"""

    ADD_SUB: Constant = 0b000
    SLL: Constant = 0b001
    SLT: Constant = 0b010
    SLTU: Constant = 0b011
    XOR: Constant = 0b100
    SRL_SRA: Constant = 0b101
    OR: Constant = 0b110
    AND: Constant = 0b111


@RvUnprivPkg.union()
class F3:
    """Funct3 encoding union"""

    branch: F3Branch
    atom: F3Atom
    arith: F3Arith


# ==============================================================================
# Funct7
# ==============================================================================


@RvUnprivPkg.enum(width=RvUnprivPkg.F7_W)
class F7Arith:
    """Funct7 encoding for arithmetic/logical operations"""

    NORMAL: Constant = 0b0000000
    SUB_SRA: Constant = 0b0100000


@RvUnprivPkg.union()
class F7:
    """Funct7 encoding union"""

    arith: F7Arith


# ==============================================================================
# Immediate Encodings
# ==============================================================================


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM5_W)
class Imm5S:
    imm_4_0: Scalar[5]


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM5_W)
class Imm5B:
    imm_11: Scalar[1]
    imm_4_1: Scalar[4]


@RvUnprivPkg.union()
class Imm5:
    s: Imm5S
    b: Imm5B


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM7_W)
class Imm7S:
    imm_11_5: Scalar[7]


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM7_W)
class Imm7B:
    imm_10_5: Scalar[6]
    imm_12: Scalar[1]


@RvUnprivPkg.union()
class Imm7:
    s: Imm7S
    b: Imm7B


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM12_W)
class Imm12I:
    imm_11_0: Scalar[12]


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM12_W)
class Imm12Shift:
    shamt: RvUnprivPkg.Shamt


@RvUnprivPkg.union()
class Imm12:
    i: Imm12I
    shift: Imm12Shift


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM20_W)
class Imm20U:
    imm_31_12: Scalar[20]


@RvUnprivPkg.struct(width=RvUnprivPkg.IMM20_W)
class Imm20J:
    imm_19_12: Scalar[8]
    imm_11: Scalar[1]
    imm_10_1: Scalar[10]
    imm_20: Scalar[1]


@RvUnprivPkg.union()
class Imm20:
    u: Imm20U
    j: Imm20J


# ==============================================================================
# Encoding Formats
# ==============================================================================


@RvUnprivPkg.struct(width=RvUnprivPkg.C_INSTR_W)
class CType:
    quad: Quad


@RvUnprivPkg.struct(width=RvUnprivPkg.INSTR_W)
class PaddedCType:
    c: CType


@RvUnprivPkg.struct(width=RvUnprivPkg.INSTR_W)
class RType:
    opcode: Opcode
    rd: RvUnprivPkg.Regsel
    f3: F3
    rs1: RvUnprivPkg.Regsel
    rs2: RvUnprivPkg.Regsel
    f7: F7


@RvUnprivPkg.struct(width=RvUnprivPkg.INSTR_W)
class IType:
    opcode: Opcode
    rd: RvUnprivPkg.Regsel
    f3: F3
    rs1: RvUnprivPkg.Regsel
    imm12: Imm12


@RvUnprivPkg.struct(width=RvUnprivPkg.INSTR_W)
class SType:
    opcode: Opcode
    imm5: Imm5
    f3: F3
    rs1: RvUnprivPkg.Regsel
    rs2: RvUnprivPkg.Regsel
    imm7: Imm7


@RvUnprivPkg.struct(width=RvUnprivPkg.INSTR_W)
class BType:
    opcode: Opcode
    imm5: Imm5
    f3: F3
    rs1: RvUnprivPkg.Regsel
    rs2: RvUnprivPkg.Regsel
    imm7: Imm7


@RvUnprivPkg.struct(width=RvUnprivPkg.INSTR_W)
class UType:
    opcode: Opcode
    rd: RvUnprivPkg.Regsel
    imm20: Imm20


@RvUnprivPkg.struct(width=RvUnprivPkg.INSTR_W)
class JType:
    opcode: Opcode
    rd: RvUnprivPkg.Regsel
    imm20: Imm20


@RvUnprivPkg.union()
class Encoding:
    c: PaddedCType
    r: RType
    i: IType
    s: SType
    b: BType
    u: UType
    j: JType
