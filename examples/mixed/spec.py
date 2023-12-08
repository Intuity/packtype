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

import packtype
from packtype import Constant, Enum, Scalar


@packtype.package()
class MyPackage:
    """My package of constants, enumerations, and data structures"""

    # Sizing
    GRID_WIDTH: Constant("Number of cells wide") = 9
    GRID_DEPTH: Constant("Number of cells deep") = 7
    # Identity
    HW_IDENTIFIER: Constant("Identifier for the device") = 0x4D594857  # MYHW
    HW_MAJOR_VERS: Constant("Major revision of the device") = 3
    HW_MINOR_VERS: Constant("Major revision of the device") = 1


@packtype.enum(package=MyPackage, mode=Enum.ONEHOT)
class DecoderState:
    """Gray-coded states of the decoder FSM"""

    DISABLED: Constant("FSM disabled")
    IDLE: Constant("Waiting for stimulus")
    HEADER: Constant("Header received")
    PAYLOAD: Constant("Payload received")


@packtype.enum(package=MyPackage, width=12)
class MessageType:
    """Different message types with explicit values"""

    PINGPONG: Constant("Ping-pong keepalive") = 0x123
    SHUTDOWN: Constant("Request system shutdown") = 0x439
    POWERUP: Constant("Request system power-up") = 0x752


@packtype.struct(package=MyPackage, width=32)
class MessageHeader:
    target_id: Scalar(width=8, desc="Target node for the message")
    msg_type: MessageType(desc="Encoded message type")


@packtype.struct(package=MyPackage)
class PingPongPayload:
    """Payload of a ping-pong keepalive message"""

    source_id: Scalar(width=8, desc="Node that sent the message")
    is_pong: Scalar(width=1, desc="Is this a ping or a pong")
    ping_value: Scalar(width=15, desc="Value to include in the response")
    timestamp: Scalar(width=8, desc="Timestamp message was sent")


@packtype.struct(package=MyPackage)
class PingPongMessage:
    """Full message including header and payload"""

    header: MessageHeader(desc="Header of the message")
    payload: PingPongPayload(desc="Payload of the message")


@packtype.union(package=MyPackage)
class MessageBus:
    """Union of the different message phases of the bus"""

    raw: Scalar(desc="Raw bus value", width=32)
    header: MessageHeader(desc="Header phase")
    ping_pong: PingPongPayload(desc="Payload of the ping-pong request")
