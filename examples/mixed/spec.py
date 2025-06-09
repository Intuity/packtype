# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import packtype
from packtype import Constant, EnumMode, Scalar


@packtype.package()
class MyPackage:
    """My package of constants, enumerations, and data structures"""

    # Sizing
    GRID_WIDTH: Constant = 9
    GRID_DEPTH: Constant = 7
    # Identity
    HW_IDENTIFIER: Constant = 0x4D594857  # MYHW
    HW_MAJOR_VERS: Constant = 3
    HW_MINOR_VERS: Constant = 1


@MyPackage.enum(mode=EnumMode.ONE_HOT)
class DecoderState:
    """Gray-coded states of the decoder FSM"""

    DISABLED: Constant
    IDLE: Constant
    HEADER: Constant
    PAYLOAD: Constant


@MyPackage.enum(width=12)
class MessageType:
    """Different message types with explicit values"""

    PINGPONG: Constant = 0x123
    SHUTDOWN: Constant = 0x439
    POWERUP: Constant = 0x752


@MyPackage.struct(width=32)
class MessageHeader:
    target_id: Scalar[8]
    msg_type: MessageType


@MyPackage.struct()
class PingPongPayload:
    """Payload of a ping-pong keepalive message"""

    source_id: Scalar[8]
    is_pong: Scalar[1]
    ping_value: Scalar[15]
    timestamp: Scalar[8]


@MyPackage.struct()
class PingPongMessage:
    """Full message including header and payload"""

    header: MessageHeader
    payload: PingPongPayload


@MyPackage.union()
class MessageBus:
    """Union of the different message phases of the bus"""

    raw: Scalar[32]
    header: MessageHeader
    ping_pong: PingPongPayload
