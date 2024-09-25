import packtype
from packtype import Constant, Scalar


@packtype.package()
class DataStructures:
    # Identity
    ID_VENDOR: Constant = 0xABCD_1234
    ID_DEVICE: Constant = 0xFEED_CAFE
    # Host-device FIFO width
    HD_FIFO_W: Constant = 64


@DataStructures.enum(width=8)
class Command:
    PING: Constant
    PONG: Constant
    STATUS: Constant


@DataStructures.struct(width=DataStructures.HD_FIFO_W)
class Header:
    command: Command
    seq_id: Scalar[7]
    length: Scalar[16]
    has_cs: Scalar


@DataStructures.union()
class Packet:
    header: Header
    payload: Scalar[64]
