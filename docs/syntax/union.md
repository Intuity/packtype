Unions are defined using the `@<PACKAGE>.union()` decorator, which processes
the definition and attaches it to the [package](package.md). Members of a union
may be declared as [scalars](scalar.md) or reference [enums](enum.md),
[structs](struct.md), or other unions.

## Example

The Packtype definition can either use a Python dataclass style or the Packtype
custom grammar:

=== "Python (.py)"

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

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        PACKET_W : Constant = 33

        struct [PACKET_W] header_t {
            command : scalar[8]
            source  : scalar[8]
            dest    : scalar[8]
            length  : scalar[8]
            parity  : scalar[1]
        }

        struct [PACKET_W] body_t {
            data   : scalar[32]
            parity : scalar[1]
        }

        union packet_t {
            raw    : scalar[PACKET_W]
            header : header_t
            body   : body_t
        }
    }
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

Union definitions expose a collection of helper functions for properties related
to the type:

 * `<UNION>._pt_width` - property that returns the bit width of the union;
 * `<UNION>._pt_mask` - property that returns a bit mask matched to the width of
   the union (i.e. `(1 << <UNION>._pt_width) - 1`);
 * `<UNION>._pt_fields` - property that returns a dictionary of fields within
   the union with the key being the field instance and the value being the
   field's name;
 * `<UNION>._pt_pack()` - packs all values contained within the union into a
   singular integer value (can also be achieved by casting to an int, e.g.
   `int(<UNION>)`);
 * `<UNION>._pt_unpack(packed: int)` - unpacks an integer value into the fields
   of the union.
