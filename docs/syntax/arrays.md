Multi-dimensional arrays are often used to represented dimensionally structured
data. Packtype's syntax allows any type to be arrayed with an arbitrary number
of dimensions and dimension sizes. The base type can be a simple [scalar](scalar.md),
or can reference a more complex type like a [struct](struct.md) or [union](union.md),
you can even reference another multi-dimensional array!

## Example

The Packtype definition can either use a Python dataclass style or the Packtype
custom grammar:

=== "Python (.py)"

    ```python linenums="1"
    import packtype
    from packtype import Constant, Scalar

    @packtype.package()
    class Package1D:
        Scalar1D : Scalar[4]

    @Package1D.struct()
    class Struct1D:
        field_a : Scalar[2]
        field_b : Scalar[3]

    @packtype.package()
    class Package3D:
        Scalar3D : Package1D.Scalar1D[4][5]
        Struct3D : Package1D.Struct1D[3][2]
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package package_1d {
        scalar_1d_t : scalar[4]

        struct struct_1d_t {
            field_a : scalar[2]
            field_b : scalar[3]
        }
    }

    package package_3d {
        scalar_3d_t : package_1d::scalar_1d_t[4][5]
        struct_3d_t : package_1d::struct_1d_t[3][2]
    }
    ```

As rendered to SystemVerilog

```sv linenums="1"
package package_1d;

typedef logic [3:0] scalar_1d_t;

typedef struct packed {
    logic [2:0] field_b;
    logic [1:0] field_a;
} struct_1d_t;

endpackage : package_1d

package package_3d;

import package_1d::scalar_1d_t;
import package_1d::struct_1d_t;

typedef scalar_1d_t [4:0][3:0] scalar_3d_t;
typedef struct_1d_t [1:0][2:0] struct_3d_t;

endpackage : package_3d
```

!!! warning

    The order of dimensions is _reversed_ when compared to declaring a packed
    multi-dimensional array in SystemVerilog. For example `scalar[4][5][6]`
    declares a 6x5 array of 4-bit elements, which in SystemVerilog would be
    written `logic [5:0][4:0][3:0]`. This is done to make it easier to parse the
    syntax, as decisions can be made reading left-to-right.

## Helper Properties and Methods

Struct definitions expose a collection of helper functions for properties related
to the type:

 * `<ARRAY>._pt_width` - property that returns the bit width of the entire array;
 * `<ARRAY>._pt_pack()` - packs all values contained within the array into a
   singular integer value (can also be achieved by casting to an int, e.g.
   `int(<ARRAY>)`);
 * `<ARRAY>._pt_unpack(packed: int)` - unpacks an integer value into the entries
   of the array;
 * `len(<ARRAY>)` - returns the size of the outermost dimension of the array;
 * `<ARRAY>[X]` - accesses element X within the array, which may return either
   an instance of the base type _or_ another packed array depending on the
   number of dimensions.
