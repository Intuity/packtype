Variants are a feature unique to the Packtype custom grammar (`.pt` files), and
allow definitions to be varied based on conditions presented to the parser. This
mechanism can be useful to allow different parts of a large project to operate
at different cadences while referring to a central set of definitions - by
allowing changes to be 'gated' on specific conditions, different consumers can
take updates at their own pace.

## Example

The example below shows how variants can be used to encapsulate two different
sizings for a bus, while common definitions can exist in just a single location:

```sv linenums="1"

package the_package {
    variants {
        "Encapsulate different options for the bus width"

        default {
            "Default condition when no variant is selected"
            DATA_BITS   : constant = 64
                "Bit-width of the data bus"
            MAX_STRIDES : constant = 4
                "Maximum number of strides of a packet"
        }

        NARROW_BUS {
            "Narrow bus variant - fewer data bits but more strides"
            DATA_BITS   : constant = 8
                "Bit width of the data bus"
            MAX_STRIDES : constant = 32
                "Maximum number of strides of a packet"
        }

    }

    DATA_BYTES : constant = DATA_BITS / 8
        "Bus width in bytes"
    STRIDE_INDEX_WIDTH : constant = clog2(MAX_STRIDES)
        "Index width to count through the strides"
}
```

If this was rendered to SystemVerilog without providing any variant conditions,
then the output would look like:

```sv linenums="1"

package the_package;

localparam DATA_BITS = 64;
localparam MAX_STRIDES = 4;
localparam DATA_BYTES = 8;
localparam STRIDE_INDEX_WIDTH = 2;

endpackage : the_package
```

While if you were to provide `NARROW_BUS` as a condition:

```sv linenums="1"

package the_package;

localparam DATA_BITS = 8;
localparam MAX_STRIDES = 32;
localparam DATA_BYTES = 1;
localparam STRIDE_INDEX_WIDTH = 5;

endpackage : the_package
```

!!! note

    While this example only shows constants being declared, any type, constant,
    or enum declaration can be made within a `variants` block just as if it was
    a native part of the package.

## Default Variant

A variants block must specify a `default` that is taken whenever no other condition
matches. If a variants block does not specify a `default`, then a `TransformerError`
will be raised during the parsing process.

Only a single `default` may be specified per variants block, specifying more than
one `default` will cause a `VariantError` to be raised.

## Variant Conditions

Variant entries can use `and` / `or` keywords to create more complex statements,
these follow the same operator precedence as Python (`and` evaluated first,
followed by `or`).

Where multiple conditions match, only the first variant block is considered.

For example:

```sv linenums="1"
package the_package {
    variants {
        COND_A and COND_B {
            X : constant = 1
        }
        COND_A {
            Y : constant = 2
        }
        default {
            Z : constant = 3
        }
    }
}
```

This means that where:

 * `COND_A` and `COND_B` are provided then ONLY `X = 1` will be evaluated;
 * `COND_A` is provided then ONLY `Y = 2` will be evaluated;
 * In any other scenario ONLY `Z = 3` will be evaluated.
