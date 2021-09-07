# Packtype

![Tests](https://github.com/Intuity/packtype/workflows/Python%20package/badge.svg)

Packtype is a Python framework for describing packed data structures for use in low-level hardware design, verification, and firmware development. From this single specification, equivalent implementations for different languages can be generated (for example C, C++, SystemVerilog).

The support matrix below shows the current support:

| Language      | Constants | Enumerations | Structures | Unions | Packages |
|---------------|:---------:|:------------:|:----------:|:------:|:--------:|
| Python        | Yes       | Yes          | Yes        | Yes    | Yes      |
| SystemVerilog | Yes       | Yes          | Yes        | Yes    | Yes      |
| C             | Yes       | Yes          | Yes        | No [1] | No [2]   |
| C++           | Yes       | Yes          | Yes        | No [1] | Yes      |

[1] While C and C++ have native support for unions, this is not used by Packtype. This is because support for true packed data structures is inconsistent across compilers, so instead Packtype uses non-packed data structures and provides methods for packing/unpacking into byte arrays.

[2] C++ uses a `namespace` construct to represent a package, but this doesn't exist in C. Instead the names of each construct are just prefixed with the name of the packag.

## Installation

The easiest way to install Packtype is to use PyPI:

```
$> python3 -m pip install packtype
```

Alternatively, you can install the latest version directly from this repository:

```
$> python3 -m pip install git+git://github.com/Intuity/packtype
```

## Using Packtype

Packtype provides the `packtype` command line utility which can be used in conjuction with a specification (detailed below) to generate the different language definitions:

```bash
# Render SystemVerilog and Python versions of the specification
$> packtype path/to/spec.py path/to/output/dir --render py --render sv
```

Two positional arguments can be provided:

 1. `SPEC` - provides the path to the Packtype specification file.
 2. `OUTDIR` - an optional path to the output folder for generated files (defaults to the current directory).

Then options are available to modify the behaviour:

 * `-r py` / `--render py` - generate the code for a certain language - the supported values are `py`, `sv`, `c`, `cpp`.
 * `--debug` - generate debug messages as the tool runs.
 * `--help` - show the help prompt.

## Examples

A number of examples are provided in the `examples` folder - each of these can be run by executing the `test.sh` file within the directory.

## Packtype Specifications

Packtype specifications use a decorators and classes to declare the different data structures. Once a specification has been written, the Packtype utility can be used to generate code for different languages.

### Decorators

The following decorators are available:

 * `@packtype.package()` - signifies a package (collection of types).
 * `@packtype.enum()` - signifies an enumeration is declared by the following class.
 * `@packtype.struct()` - signifies a structure is declared by the following class.
 * `@packtype.union()` - signifies a union is declared by the following class.

The `@packtype.enum()`, `@packtype.struct()`, and `@packtype.union()` decorators all accept the following arguments:

 * `package=MyPackage` - associates the enum, struct, or union with the named package.
 * `width=32` - declares the bit width of the enum, struct, or union - if omitted this is determined automatically.

These decorators and arguments are demonstrated in the examples below.

### Package

Constants, enumerations, structures, and unions must be associated to a named package - this helps to cleanly namespace the generated types as a project grows.

```python
import packtype

@packtype.package()
class MyPackage:
    """ My package of constants, enumerations, and data structures """
    pass
```

### Constants

Numeric constants can be attached to the root of a package to share fixed values between different parts of implementation, verification, and firmware.

```python
import packtype
from packtype import Constant

@packtype.package()
class MyPackage:
    """ My package of constants, enumerations, and data structures """
    # Sizing
    GRID_WIDTH : Constant("Number of cells wide") = 9
    GRID_DEPTH : Constant("Number of cells deep") = 7
    # Identity
    HW_IDENTIFIER : Constant("Identifier for the device"   ) = 0x4D594857 # MYHW
    HW_MAJOR_VERS : Constant("Major revision of the device") = 3
    HW_MINOR_VERS : Constant("Major revision of the device") = 1
```

### Enumerations

Enumerations can be declared with explicit or automatically incrementing values. Different modes of enumeration are provided for convenience, which are selected using the `mode=Enum.INDEXED` argument to the `@packtype.enum()` decorator:

 * `INDEXED` - Each value increments by one, starting at zero.
 * `ONEHOT` - Each value sets exactly one bit position high (e.g. `1`, `2`, `4`, `8`).
 * `GRAY` - Values form a Gray code where only one bit flips between any two consecutive values.

```python
import packtype
from packtype import Enum

# ...declaration of package...

@packtype.enum(package=MyPackage, mode=Enum.ONEHOT)
class DecoderState:
    """ Gray-coded states of the decoder FSM """
    DISABLED : Constant("FSM disabled"        )
    IDLE     : Constant("Waiting for stimulus")
    HEADER   : Constant("Header received"     )
    PAYLOAD  : Constant("Payload received"    )

@packtype.enum(package=MyPackage, width=12)
class MessageType:
    """ Different message types with explicit values """
    PINGPONG : Constant("Ping-pong keepalive"    ) = 0x123
    SHUTDOWN : Constant("Request system shutdown") = 0x439
    POWERUP  : Constant("Request system power-up") = 0x752
```

### Structs

Packed data structures can be declared with fixed size scalar fields, or with references to other data structures and enumerated values.

```python
import packtype
from packtype import Scalar

# ...declaration of package...

@packtype.struct(package=MyPackage, width=32)
class MessageHeader:
    """ Common header for all messages """
    target_id : Scalar(width=8, desc="Target node for the message")
    msg_type  : MessageType(desc="Encoded message type")

@packtype.struct(package=MyPackage) # Width calculated from field sizes
class PingPongPayload:
    """ Payload of a ping-pong keepalive message """
    source_id  : Scalar(width= 8, desc="Node that sent the message")
    is_pong    : Scalar(width= 1, desc="Is this a ping or a pong")
    ping_value : Scalar(width=15, desc="Value to include in the response")
    timestamp  : Scalar(width= 8, desc="Timestamp message was sent")

@packtype.struct(package=MyPackage)
class PingPongMessage:
    """ Full message including header and payload """
    header  : MessageHeader("Header of the message")
    payload : PingPongPayload("Payload of the message")
```

By default, fields are packed into data structures from the LSB - but this can be reversed to pack from the MSB by providing the `pack=Struct.FROM_MSB` argument to the decorator. When using this mode, the `width` of the data structure must be explicitly specified. For example:

```python
import packtype
from packtype import Scalar, Struct

@packtype.struct(package=MyPackage, pack=Struct.FROM_MSB, width=32)
class PingPongPayload:
    """ Payload of a ping-pong keepalive message """
    source_id  : Scalar(width= 8, desc="Node that sent the message")
    is_pong    : Scalar(width= 1, desc="Is this a ping or a pong")
    ping_value : Scalar(width=15, desc="Value to include in the response")
    timestamp  : Scalar(width= 8, desc="Timestamp message was sent")
```

### Unions

Unions allow different data structures to be overlapped on the same data - this is especially useful in protocol decoders where a bus may carry different formats and structures of data in different cycles. All components of a union must be of the same size, otherwise the tool will raise an error.

**NOTE:** It is not possible to support unions in all languages due to their poor native support for packed data types, check the compatibility matrix above for details.

```python
import packtype
from packtype import Scalar

@packtype.union(package=MyPackage)
class MessageBus:
    """ Union of the different message phases of the bus """
    raw       : Scalar(desc="Raw bus value", width=32)
    header    : MessageHeader(desc="Header phase")
    ping_pong : PingPongPayload(desc="Payload of the ping-pong request")
```
