# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
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

from lark import Transformer, v_args

from packtype.enum import EnumMode
from packtype.grammar.expression import DeclExpr
from packtype.grammar.declarations import (
    Signedness,
    Position,
    DeclImport,
    DeclAlias,
    DeclConstant,
    DeclScalar,
    DeclEnum,
    DeclField,
    DeclStruct,
    DeclUnion,
    DeclPackage,
)


class PacktypeTransformer(Transformer):

    def SIGNED_INT(self, body):
        return int(body)

    def HEX(self, body):
        return int(body, 16)

    def OPERATOR(self, body):
        return str(body)

    def expr(self, body):
        if len(body) == 3:
            return DeclExpr.operate(*body)
        else:
            return DeclExpr(body[0])

    def signed(self, *_):
        return Signedness.SIGNED

    def unsigned(self, *_):
        return Signedness.UNSIGNED

    def enum_mode_indexed(self, *_):
        return EnumMode.INDEXED

    def enum_mode_onehot(self, *_):
        return EnumMode.ONE_HOT

    def enum_mode_gray(self, *_):
        return EnumMode.GRAY

    def CNAME(self, body):
        return str(body)

    def descr(self, body):
        return str(body[0]).strip('"')

    @v_args(meta=True)
    def decl_import(self, meta, body):
        return DeclImport(Position(meta.line, meta.column), *body)

    @v_args(meta=True)
    def decl_alias(self, meta, body):
        return DeclAlias(Position(meta.line, meta.column), *body)

    @v_args(meta=True)
    def decl_constant(self, meta, body):
        c_type, *remainder = body
        if c_type == "SIZED_CONSTANT":
            width, expr = remainder
        else:
            width = None
            expr = remainder[0]
        return DeclConstant(Position(meta.line, meta.column), c_type, width, expr)

    @v_args(meta=True)
    def field(self, meta, body):
        return body[0] if isinstance(body[0], DeclScalar) else DeclField(Position(meta.line, meta.column),*body)

    @v_args(meta=True)
    def decl_enum(self, meta, body):
        e_type, *remainder = body
        # Pickup mode if given
        if remainder and isinstance(remainder[0], EnumMode):
            mode, *remainder = remainder
        else:
            mode = EnumMode.INDEXED
        # Pickup width if given
        if remainder and isinstance(remainder[0], int):
            width, *remainder = remainder
        else:
            width = None
        # Pickup description if given
        if remainder and isinstance(remainder[0], str):
            description, *remainder = remainder
        else:
            description = None
        return DeclEnum(Position(meta.line, meta.column), e_type, mode, width, description, remainder)

    @v_args(meta=True)
    def decl_scalar(self, meta, body):
        s_type, *remainder = body
        # Pickup signedness
        if remainder and isinstance(remainder[0], Signedness):
            signed, *remainder = remainder
        else:
            signed = Signedness.UNSIGNED
        # Pickup width
        if remainder:
            width = remainder[0]
        else:
            width = 1
        return DeclScalar(Position(meta.line, meta.column), s_type, signed, width)

    @v_args(meta=True)
    def decl_struct(self, meta, body):
        # Extract width if given
        if isinstance(body[0], int):
            width, name, *remainder = body
        else:
            width = None
            name, *remainder = body
        # Extract description if given
        if isinstance(remainder[0], str):
            description, *fields = remainder
        else:
            description = None
            fields = remainder
        return DeclStruct(Position(meta.line, meta.column), name, width, description, fields)

    @v_args(meta=True)
    def decl_union(self, meta, body):
        # Extract name and description
        if isinstance(body[0], str):
            name, *remainder = body
            description = None
        else:
            name, description, *remainder = body
        # Fields are the rest of the body
        fields = remainder
        return DeclUnion(Position(meta.line, meta.column), name, description, fields)

    @v_args(meta=True)
    def decl_package(self, meta, body):
        p_name, *remainder = body
        # Extract description if given
        if isinstance(remainder[0], str):
            description, *remainder = remainder
        else:
            description = None
        return DeclPackage(Position(meta.line, meta.column), p_name, description, remainder)
