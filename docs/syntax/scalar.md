Scalars are the most simple definition of a type as they describe a single
dimensioned bitvector. They are declared using the `Scalar` type and can be
declared within [packages](package.md) or [structs](struct.md).

## Example

The Packtype definition can either use a Python dataclass style or the Packtype
custom grammar:

=== "Python (.py)"

    ```python linenums="1"
    import packtype
    from packtype import Constant, Scalar

    @packtype.package()
    class MyPackage:
        # Constants
        TYPE_A_W : Constant = 29
        TYPE_B_W : Constant = 13

        # Typedefs
        TypeA : Scalar[TYPE_A_W]
        TypeB : Scalar[TYPE_B_W]
        TypeC : Scalar[7]
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        // Constants
        TYPE_A_W : constant = 29
        TYPE_B_W : constant = 13

        // Typedefs
        TypeA : Scalar[TYPE_A_W]
            "Comments can be attached to scalar types"
        TypeB : Scalar[TYPE_B_W]
            "They can be queried from the digested result"
        TypeC : Scalar[7]
            """
            Multiline comments can be used for long descriptions.
            Use triple quotes for these like with Python docstrings.
            """
    }
    ```

As rendered to SystemVerilog:

```sv linenums="1"
package my_package;

localparam TYPE_A_W = 29;
localparam TYPE_B_W = 13;

typedef logic [28:0] type_a_t;
typedef logic [12:0] type_b_t;
typedef logic [6:0] type_c_t;

endpackage : my_package
```

!!! note

    Packtype currently processes the width of the scalar at the point of definition,
    hence when rendered it does not visibly refer to `TYPE_A_W` but it is internally
    consistent with the definition.

## Syntax

Scalars must be defined with an explicit bit width expressed within the square
brackets (`[...]`) following the `Scalar` keyword. The width must be a positive
integer value, and may be either hardcoded or refer to a [constant](constant.md)
or an expression. A second optional boolean parameter may be provided that
encodes whether the scalar is signed (`True`) or unsigned (`False`), defaulting
to unsigned.

```python
@packtype.package()
class MyPackage:
    # Format: <NAME> : Scalar[<WIDTH>, <SIGNED>]
    MyType : Scalar[123, False]
```

## Helper Properties and Methods

Scalar definitions expose a collection of helper functions for properties related
to the type:

 * `<Scalar>._pt_width` - property that returns the bit width of the type;
 * `<Scalar>._pt_signed` - property that returns whether the scalar expresses a
   signed or unsigned type;
 * `<Scalar>._pt_mask` - property that returns a bit mask matched to the width of
   the type (i.e. `(1 << MyScalar._pt_width) - 1`).
