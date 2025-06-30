Unions are defined using the `@<PACKAGE>.union()` decorator, which processes
the definition and attaches it to the [package](package.md). Members of a union
may be declared as [scalars](scalar.md) or reference [enums](enum.md), 
[structs](struct.md), or other unions.

## Example

The packtype definition: 

```python linenums="1"
import packtype
from packtype import Constant, Scalar

@packtype.package()
class MyPackage:
    PACKET_W : Constant = 33

@MyPackage.struct(width=MyPackage.PACKET_W)
class Header:
    command : Scalar[8]
    source  : Scalar[8]
    dest    : Scalar[8]
    length  : Scalar[8]
    parity  : Scalar[1]

@MyPackage.struct(width=MyPackage.PACKET_W)
class Body:
    data   : Scalar[32]
    parity : Scalar[1]

@MyPackage.union()
class Packet:
    raw    : Scalar[MyPackage.PACKET_W]
    header : Header
    body   : Body
```

As rendered to SystemVerilog

```sv linenums="1"
package my_package;

// ...supporting declarations...

typedef union packed {
    logic [32:0] raw;
    header_t     header;
    body_t       body;
} packet_t;

endpackage : my_package
```

!!! note

    All members of a union must have the same bit width, otherwise a `UnionError`
    will be raised for the first field that differs.

## Helper Properties and Methods

Struct definitions expose a collection of helper functions for properties related
to the type:

 * `<STRUCT>._pt_width` - property that returns the bit width of the struct;
 * `<STRUCT>._pt_mask` - property that returns a bit mask matched to the width of
   the struct (i.e. `(1 << <STRUCT>._pt_width) - 1`);
 * `<STRUCT>._pt_fields` - property that returns a dictionary of fields within
   the struct with the key being the field instance and the value being the 
   field's name;
 * `<STRUCT>._pt_pack()` - packs all values contained within the struct into a
   singular integer value (can also be achieved by casting to an int, e.g.
   `int(<STRUCT>)`);
 * `<STRUCT>._pt_unpack(packed: int)` - unpacks an integer value into the fields
   of the struct.
