# Packtype

![Tests](https://github.com/Intuity/packtype/workflows/Python%20package/badge.svg)

Packtype is a Python framework for describing packed data structures for use in low-level hardware design, verification, and firmware development. From this single specification, equivalent implementations for different languages can be generated (for example C, C++, SystemVerilog).

The support matrix below shows the current support:

| Language      | Constants | Enumerations | Structures | Unions | Packages |
|---------------|:---------:|:------------:|:----------:|:------:|:--------:|
| Python        | Yes       | Yes          | Yes        | Yes    | Yes      |
| SystemVerilog | Yes       | Yes          | Yes        | Yes    | Yes      |

**NOTE** Support for C and C++ is currently missing from version 2, but was present in version 1 - this regression will be addressed in a future revision.

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
$> packtype path/to/spec.py path/to/output/dir --render sv
```

Two positional arguments can be provided:

 1. `SPEC` - provides the path to the Packtype specification file.
 2. `OUTDIR` - an optional path to the output folder for generated files (defaults to the current directory).

Then options are available to modify the behaviour:

 * `-r sv` / `--render sv` - generate the code for a certain language - only `sv` is currently supported, further languages will be added in due course.
 * `--debug` - generate debug messages as the tool runs.
 * `--help` - show the help prompt.

## Examples

A number of examples are provided in the `examples` folder - each of these can be run by executing the `test.sh` file within the directory.

## Packtype Specifications

Packtype specifications use a decorators and classes to declare the different data structures. Once a specification has been written, the Packtype utility can be used to generate code for different languages.

### Package Declaration

Packages are signified using the ``@packtype.package()`` decorator, this declares
a root object onto which constants, typedefs, enums, structs, and unions can be
bound.

```python
import packtype

@packtype.package()
class SomeProtocolPkg:
    """Contains definitions for some protocol"""
    ...
```

### Constants

Numeric constants can be attached to the root of a package to share fixed values between different parts of implementation, verification, and firmware.

```python
import packtype
from packtype import Constant

@packtype.package()
class SomeProtocolPkg:
    """Contains definitions for some protocol"""
    ADDRESS_WIDTH : Constant = 16
    DATA_WIDTH    : Constant = 32
    SIZE_WIDTH    : Constant = 8
```

### Typedefs

Simple bitvector types can be declared within a package using the `Scalar` type,
the parameterisation determines the bit-width of the structure:

```python
import packtype
from packtype import Constant, Scalar

@packtype.package()
class SomeProtocolPkg:
    """Contains definitions for some protocol"""
    # Constants
    ADDRESS_WIDTH : Constant = 16
    # Simple Types
    Address : Scalar[ADDRESS_WIDTH]
```

### Enumerations

Enumerations are declared using the `@<PKG>.enum()` decorator and can accept the
following two attributes:

 * `width` - sets a fixed bit-width of the enumeration, this must be a positive integer;
 * `mode` - sets how entries of the enumeration are assigned values, the supported modes are:

   * `EnumMode.INDEXED` - Each value increments by one, starting at zero.
   * `EnumMode.ONE_HOT` - Each value sets exactly one bit position high (e.g. `1`, `2`, `4`, `8`).
   * `EnumMode.GRAY` - Values form a Gray code where only one bit flips between any two consecutive values.

Enumerations can either be declared with explicit or automatically incrementing
values, or a mix of the two.

```python
import packtype
from packtype import EnumMode

@packtype.package()
class DecoderPkg:
    ...

@DecoderPkg.enum(width=12)
class MessageType:
    """ Different message types with explicit values """
    PINGPONG : Constant = 0x123
    SHUTDOWN : Constant = 0x439
    POWERUP  : Constant = 0x752

@DecoderPkg.enum(mode=Enum.GRAY)
class DecoderState:
    """ Gray-coded states of the decoder FSM """
    DISABLED : Constant
    IDLE     : Constant
    HEADER   : Constant
    PAYLOAD  : Constant
```

### Structs

Structs are declared using the `@<PKG>.struct()` decorator and can contain any
number of fields that are simple scalar values, enumerations, or nested structs
or unions. The decorator supports the following attributes:

 * `width` - sets a fixed bit-width of the struct, this must be a positive integer;
 * `packing` - determines the order in which declared fields are placed in the packed version:
    * `Packing.FROM_LSB` - place fields starting at the least-significant bit;
    * `Packing.FROM_MSB` - place fields starting from the most-significant bit.

```python
import packtype
from packtype import Scalar

@packtype.package()
class DecoderPkg:
    ...

@DecoderPkg.struct(width=32)
class MessageHeader:
    """ Common header for all messages """
    target_id : Scalar[8]
    msg_type  : MessageType

@DecoderPkg.struct() # Width calculated from field sizes
class PingPongPayload:
    """ Payload of a ping-pong keepalive message """
    source_id  : Scalar[ 8]
    is_pong    : Scalar[ 1]
    ping_value : Scalar[15]
    timestamp  : Scalar[ 8]

@DecoderPkg.struct()
class PingPongMessage:
    """ Full message including header and payload """
    header  : MessageHeader
    payload : PingPongPayload
```

By default, fields are packed into data structures from the LSB - but this can be reversed to pack from the MSB by providing the `packing=Packing.FROM_MSB` argument to the decorator. For example:

```python
import packtype
from packtype import Packing, Scalar

@packtype.package()
class DecoderPkg:
    ...

@DecoderPkg.struct(package=MyPackage, packing=Packing.FROM_MSB, width=32)
class PingPongPayload:
    """ Payload of a ping-pong keepalive message """
    source_id  : Scalar[ 8]
    is_pong    : Scalar[ 1]
    ping_value : Scalar[15]
    timestamp  : Scalar[ 8]
```

### Unions

Unions allow different data structures to form different projections over the same raw bits - this is especially useful in protocol decoders where a bus may carry different formats and structures of data in different cycles. All components of a union must be of the same size, otherwise the tool will raise an error.

```python
import packtype
from packtype import Scalar

@packtype.package()
class DecoderPkg:
    ...

@DecoderPkg.union()
class MessageBus:
    """ Union of the different message phases of the bus """
    raw       : Scalar[32]
    header    : MessageHeader
    ping_pong : PingPongPayload
```
