from datastructures import DataStructures, Packet

import packtype
import packtype.registers
from packtype import Constant, Scalar
from packtype.registers import Behaviour

# === Device Identity, Version, and Status ===


@packtype.registers.register(behaviour=Behaviour.CONSTANT)
class Identity:
    vendor: Constant[32] = DataStructures.ID_VENDOR
    device: Constant[32] = DataStructures.ID_DEVICE


@packtype.registers.register(behaviour=Behaviour.DATA_I2X)
class Version:
    """Encodes the version number as <PRIMARY>.<SECONDARY.<TERTIARY> #<BUILD>"""

    primary: Constant[16] = 4
    secondary: Constant[8] = 3
    tertiary: Constant[8] = 9
    build: Scalar[16]


@packtype.registers.register(behaviour=Behaviour.DATA_I2X)
class Status:
    active: Scalar[1]
    fault: Scalar[1]


@packtype.registers.group()
class DeviceGroup:
    identity: Identity
    version: Version
    status: Status


# === Device Control ===


@packtype.registers.register(behaviour=Behaviour.DATA_X2I)
class ResetControl:
    asserted: Scalar[1]


@packtype.registers.group()
class ControlGroup:
    core_reset: 4 * ResetControl


# === Communications ===


@packtype.registers.register(behaviour=Behaviour.FIFO_X2I)
class HostToDevice:
    data: Packet


@packtype.registers.register(behaviour=Behaviour.FIFO_I2X)
class DeviceToHost:
    data: Packet


@packtype.registers.group()
class CommsGroup:
    h2d: HostToDevice
    d2h: DeviceToHost


# === Register File ===


@packtype.registers.file(width=64)
class Control:
    device: DeviceGroup
    control: ControlGroup
    comms: 2 * CommsGroup
