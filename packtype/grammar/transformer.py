# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math

from lark import Transformer, v_args

from ..common import utils
from ..types.assembly import Packing
from ..types.enum import EnumMode
from .declarations import (
    DeclAlias,
    DeclConstant,
    DeclEnum,
    DeclField,
    DeclImport,
    DeclPackage,
    DeclScalar,
    DeclStruct,
    DeclUnion,
    Description,
    Position,
    Signed,
    Unsigned,
)
from .expression import DeclExpr, DeclExprFunction


class PacktypeTransformer(Transformer):
    def DECIMAL(self, body):  # noqa: N802
        return int(body, 10)

    def HEX(self, body):  # noqa: N802
        return int(body, 16)

    def BINARY(self, body):  # noqa: N802
        return int(body, 2)

    def OPERATOR(self, body):  # noqa: N802
        return str(body)

    def expr_funcs(self, body):
        method, *args = body
        match method.lower():
            case "clog2":
                method_func = utils.clog2
            case "width":
                method_func = utils.width
            case _:
                method_func = getattr(math, method, None)
        return DeclExprFunction(method_func, *args)

    def expr(self, body):
        return DeclExpr.digest(body)

    def signed(self, *_):
        return Signed

    def unsigned(self, *_):
        return Unsigned

    def enum_mode_indexed(self, *_):
        return EnumMode.INDEXED

    def enum_mode_onehot(self, *_):
        return EnumMode.ONE_HOT

    def enum_mode_gray(self, *_):
        return EnumMode.GRAY

    def packing_mode_lsb(self, *_):
        return Packing.FROM_LSB

    def packing_mode_msb(self, *_):
        return Packing.FROM_MSB

    def CNAME(self, body):  # noqa: N802
        return str(body)

    def descr(self, body):
        return Description(str(body[0]).strip('"'))

    @v_args(meta=True)
    def decl_import(self, meta, body):
        return DeclImport(Position(meta.line, meta.column), *body)

    @v_args(meta=True)
    def decl_alias(self, meta, body):
        return DeclAlias(Position(meta.line, meta.column), *body)

    @v_args(meta=True)
    def decl_constant(self, meta, body):
        if len(body) == 3:
            c_type, width, expr = body
        else:
            c_type, expr = body
            width = None
        return DeclConstant(Position(meta.line, meta.column), c_type, width, expr)

    @v_args(meta=True)
    def field(self, meta, body):
        return (
            body[0]
            if isinstance(body[0], DeclScalar)
            else DeclField(Position(meta.line, meta.column), *body)
        )

    @v_args(meta=True)
    def enum_body_assign(self, meta, body):
        return DeclConstant(Position(meta.line, meta.column), body[0], None, body[1])

    @v_args(meta=True)
    def decl_enum(self, meta, body):
        remainder = body
        # Pickup mode if given
        if remainder and isinstance(remainder[0], EnumMode):
            mode, *remainder = remainder
        else:
            mode = EnumMode.INDEXED
        # Pickup width if given
        if remainder and isinstance(remainder[0], DeclExpr):
            width, *remainder = remainder
        else:
            width = None
        # Pickup type
        e_type, *remainder = remainder
        # Pickup description if given
        if remainder and isinstance(remainder[0], Description):
            description, *remainder = remainder
        else:
            description = None
        return DeclEnum(
            Position(meta.line, meta.column), e_type, mode, width, description, remainder
        )

    @v_args(meta=True)
    def decl_scalar(self, meta, body):
        s_type, *remainder = body
        # Pickup signedness
        if remainder and (remainder[0] is Signed or remainder[0] is Unsigned):
            signed, *remainder = remainder
        else:
            signed = Unsigned
        # Pickup width
        if remainder:
            width = remainder[0]
        else:
            width = DeclExpr(1)
        return DeclScalar(Position(meta.line, meta.column), s_type, signed, width)

    @v_args(meta=True)
    def decl_struct(self, meta, body):
        remainder = body
        # Extract packing mode if given
        if isinstance(remainder[0], Packing):
            packing, *remainder = remainder
        else:
            packing = Packing.FROM_LSB
        # Extract width if given
        if isinstance(remainder[0], DeclExpr):
            width, name, *remainder = remainder
        else:
            width = None
            name, *remainder = remainder
        # Extract description if given
        if isinstance(remainder[0], Description):
            description, *fields = remainder
        else:
            description = None
            fields = remainder
        return DeclStruct(
            Position(meta.line, meta.column), name, packing, width, description, fields
        )

    @v_args(meta=True)
    def decl_union(self, meta, body):
        # Extract name
        name, *remainder = body
        # Extract description if given
        if remainder and isinstance(remainder[0], Description):
            description, *fields = remainder
        else:
            fields = remainder
            description = None
        return DeclUnion(Position(meta.line, meta.column), name, description, fields)

    @v_args(meta=True)
    def decl_package(self, meta, body):
        p_name, *remainder = body
        # Extract description if given
        if remainder and isinstance(remainder[0], Description):
            description, *remainder = remainder
        else:
            description = None
        return DeclPackage(Position(meta.line, meta.column), p_name, description, remainder)
