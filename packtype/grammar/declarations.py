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

from dataclasses import dataclass
from enum import Enum, auto


class Signedness(Enum):
    UNSIGNED = auto()
    SIGNED = auto()


@dataclass()
class Position:
    line: int
    column: int


@dataclass()
class DeclImport:
    position: Position
    package: str
    type: str


@dataclass()
class DeclAlias:
    position: Position
    local: str
    foreign: str


@dataclass()
class DeclConstant:
    position: Position
    type: str
    width: int
    expr: str


@dataclass()
class DeclScalar:
    position: Position
    type: str
    signedness: Signedness
    width: int


@dataclass()
class DeclEnum:
    position: Position
    type: str
    mode: str
    width: int
    description: str
    values: list


@dataclass()
class DeclField:
    position: Position
    name: str
    type: str


@dataclass()
class DeclStruct:
    position: Position
    name: str
    width: int
    description: str
    fields: list


@dataclass()
class DeclUnion:
    position: Position
    name: str
    description: str
    fields: list


@dataclass()
class DeclPackage:
    position: Position
    name: str
    description: str
    declarations: list
