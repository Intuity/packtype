# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import math

from lark import Transformer, v_args

from .. import utils
from ..common.expression import Expression, ExpressionFunction
from ..types.assembly import Packing
from ..types.enum import EnumMode
from .declarations import (
    DeclAlias,
    DeclConstant,
    DeclDimensions,
    DeclEnum,
    DeclField,
    DeclImport,
    DeclInstance,
    DeclPackage,
    DeclScalar,
    DeclStruct,
    DeclUnion,
    Description,
    FieldAssignment,
    FieldAssignments,
    ForeignRef,
    Modifier,
    Position,
    Signed,
    Unsigned,
)


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
                method_func = utils.get_width
            case _:
                method_func = getattr(math, method, None)
        return ExpressionFunction(method_func, *args)

    def expr(self, body):
        return Expression.digest(body)

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

    def modifier(self, body):
        return Modifier(*body)

    def dimension(self, body):
        return body[0]

    def dimensions(self, body):
        return DeclDimensions(dimensions=body)

    def foreign_ref(self, body):
        return ForeignRef(*body)

    def field_assignment(self, body):
        return FieldAssignment(*body)

    def field_assignments(self, body):
        return FieldAssignments(assignments=body)

    @v_args(meta=True)
    def decl_import(self, meta, body):
        return DeclImport(Position(meta.line, meta.column), *body)

    @v_args(meta=True)
    def decl_alias(self, meta, body):
        name = body.pop(0)
        ref = body.pop(0)
        dimensions = body.pop(0) if body and isinstance(body[0], DeclDimensions) else None
        if body and isinstance(body[0], Expression | FieldAssignments):
            return DeclInstance(
                Position(meta.line, meta.column),
                name,
                ref,
                body[0],
                body[1] if len(body) > 1 else None,
            )
        else:
            return DeclAlias(
                Position(meta.line, meta.column), name, ref, dimensions, body[0] if body else None
            )

    @v_args(meta=True)
    def decl_constant(self, meta, body):
        # Extract constant name
        c_type, *remainder = body
        # Extract optional width and constant value
        if (
            len(remainder) >= 2
            and isinstance(remainder[0], Expression)
            and isinstance(remainder[1], Expression)
        ):
            width, expr, *remainder = remainder
        else:
            width = None
            expr, *remainder = remainder
        # Extract optional description
        descr = None
        if remainder and isinstance(remainder[0], Description):
            descr = remainder[0]
        return DeclConstant(Position(meta.line, meta.column), c_type, width, expr, descr)

    @v_args(meta=True)
    def field(self, meta, body):
        if isinstance(body[0], DeclScalar):
            return body[0]
        else:
            return DeclField(
                Position(meta.line, meta.column),
                name=body.pop(0),
                ref=body.pop(0),
                dimensions=body.pop(0) if body and isinstance(body[0], DeclDimensions) else None,
                description=body.pop(0) if body and isinstance(body[0], Description) else None,
            )

    @v_args(meta=True)
    def enum_body_simple(self, meta, body):
        return DeclConstant(
            position=Position(meta.line, meta.column),
            name=body[0],
            width=None,
            expr=None,
            description=body[1] if len(body) > 1 else None,
        )

    @v_args(meta=True)
    def enum_body_assign(self, meta, body):
        return DeclConstant(
            position=Position(meta.line, meta.column),
            name=body[0],
            width=None,
            expr=body[1],
            description=body[2] if len(body) > 2 else None,
        )

    @v_args(meta=True)
    def enum_body_typed(self, meta, body):
        return DeclConstant(
            position=Position(meta.line, meta.column),
            name=body[0],
            width=None,
            expr=None,
            description=body[1] if len(body) > 1 else None,
        )

    @v_args(meta=True)
    def decl_enum(self, meta, body):
        remainder = body
        # Pickup mode if given
        if remainder and isinstance(remainder[0], EnumMode):
            mode, *remainder = remainder
        else:
            mode = EnumMode.INDEXED
        # Pickup width if given
        if remainder and isinstance(remainder[0], Expression):
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
        # Pickup modifiers
        mods = []
        while remainder and isinstance(remainder[0], Modifier):
            mods.append(remainder.pop(0))
        return DeclEnum(
            Position(meta.line, meta.column),
            e_type,
            mode,
            width,
            description,
            mods,
            remainder,
        )

    @v_args(meta=True)
    def decl_scalar(self, meta, body):
        s_type, *remainder = body
        # Pickup signedness
        if remainder and (remainder[0] is Signed or remainder[0] is Unsigned):
            signed, *remainder = remainder
        else:
            signed = Unsigned
        # Pickup dimensions
        if remainder and isinstance(remainder[0], DeclDimensions):
            dimensions, *remainder = remainder
        else:
            dimensions = DeclDimensions(dimensions=[Expression(1)])
        # Pickup description
        if remainder and isinstance(remainder[0], Description):
            descr = remainder[0]
        else:
            descr = None
        return DeclScalar(Position(meta.line, meta.column), s_type, signed, dimensions, descr)

    @v_args(meta=True)
    def decl_struct(self, meta, body):
        remainder = body
        # Extract packing mode if given
        if isinstance(remainder[0], Packing):
            packing, *remainder = remainder
        else:
            packing = Packing.FROM_LSB
        # Extract width if given
        if isinstance(remainder[0], Expression):
            width, name, *remainder = remainder
        else:
            width = None
            name, *remainder = remainder
        # Extract description if given
        if isinstance(remainder[0], Description):
            description, *remainder = remainder
        else:
            description = None
        # Extract modifiers
        mods = []
        while remainder and isinstance(remainder[0], Modifier):
            mods.append(remainder.pop(0))
        return DeclStruct(
            Position(meta.line, meta.column), name, packing, width, description, mods, remainder
        )

    @v_args(meta=True)
    def decl_union(self, meta, body):
        # Extract name
        name, *remainder = body
        # Extract description if given
        if remainder and isinstance(remainder[0], Description):
            description, *remainder = remainder
        else:
            description = None
        # Extract modifiers
        mods = []
        while remainder and isinstance(remainder[0], Modifier):
            mods.append(remainder.pop(0))
        return DeclUnion(Position(meta.line, meta.column), name, description, mods, remainder)

    @v_args(meta=True)
    def decl_package(self, meta, body):
        p_name, *remainder = body
        # Extract description if given
        if remainder and isinstance(remainder[0], Description):
            description, *remainder = remainder
        else:
            description = None
        # Extract modifiers
        mods = []
        while remainder and isinstance(remainder[0], Modifier):
            mods.append(remainder.pop(0))
        return DeclPackage(Position(meta.line, meta.column), p_name, description, mods, remainder)

    def root(self, body):
        return body
