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

from random import randint, choice

import pytest

from packtype import Constant, Enum, Scalar, Struct
from packtype.container import Container

from .common import random_str

def test_container_check():
    """ Test that a container correctly tests legal items """
    inst = Container(random_str(10), {}, legal=[Constant, Scalar])
    assert inst._pt_check(Constant())
    assert inst._pt_check(Scalar())
    assert not inst._pt_check(Enum(random_str(10), {}))
    assert not inst._pt_check(Struct(random_str(10), {}))

def test_container_check_skip():
    """ If no legal items supplied, container should always approve """
    inst = Container(random_str(10), {})
    assert inst._pt_check(Constant())
    assert inst._pt_check(Scalar())
    assert inst._pt_check(Enum(random_str(10), {}))
    assert inst._pt_check(Struct(random_str(10), {}))
