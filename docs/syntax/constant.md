Constants are defined using the `Constant` type and are declared directly within
the [package](package.md). They carry a fixed value, which may be computed from
other constants, and may be given an explicit bit width.

## Example

The Packtype definition can either use a Python dataclass style or the Packtype
custom grammar:

=== "Python (.py)"

    ```python linenums="1"
    import packtype
    from packtype import Constant

    @packtype.package()
    class MyPackage:
        VALUE_A : Constant = 123
        VALUE_B : Constant[16] = 234
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        VALUE_A : constant = 123
            "Comments may be attached to values with a string following the definition"
        VALUE_B : constant[16] = 234
            "These are attached to the constant definitions"
        VALUE_C: constant[2] = 3
            """
            Multiline comments can be used for long descriptions.
            Use triple quotes for these like with Python docstrings.
            """
    }
    ```

As rendered to SystemVerilog:

```sv linenums="1"
package my_package;

localparam VALUE_A = 123;
localparam bit [15:0] VALUE_B = 234;

endpackage : my_package
```

## Syntax

### Unsized Constants

A constant defined without an explicit size will be treated as unsized and it
will be left to the target language template to decide what size container to
allocate it.

=== "Python (.py)"

    ```python linenums="1"
    @packtype.package()
    class MyPackage:
        # Format: <NAME> : Constant = <VALUE>
        MY_CONSTANT : Constant = 123
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        // Format: <NAME> : constant = <VALUE>
        MY_CONSTANT : constant = 123
    }
    ```

### Implicit Constants

Unsized constants may be declared implicitly by omitting the `: Constant` keyword
from the declaration:

```python linenums="1"
@packtype.package()
class MyPackage:
    # Format: <NAME> = <VALUE>
    MY_CONSTANT = 123
```

!!! note

    This is only supported in the Python dataclass style syntax

### Sized Constants

Constants may be defined with an explicit bit width, in which case Packtype will
respect the request bit width internally and target language templates will
allocate the nearest possible size large enough to hold the full range of that
number of bits.

=== "Python (.py)"

    ```python linenums="1"
    @packtype.package()
    class MyPackage:
        # Format: <NAME> : Constant[<WIDTH>] = <VALUE>
        MY_CONSTANT : Constant[8] = 123
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        // Format: <NAME> : constant[<WIDTH>] = <VALUE>
        MY_CONSTANT : constant[8] = 123
    }
    ```

## Expressions

Both the width and value assignment for a constant declaration may be computed
from other constant definitions within the package.

=== "Python (.py)"

    ```python linenums="1"
    @packtype.package()
    class MyPackage:
        DOUBLE_WIDTH : Constant = 32
        VALUE_A      : Constant = 9
        VALUE_B      : Constant = 3
        COMPUTED     : Constant[DOUBLE_WIDTH // 2] = (VALUE_A * VALUE_B) + 1
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        DOUBLE_WIDTH : constant = 32
        VALUE_A      : constant = 9
        VALUE_B      : constant = 3
        COMPUTED     : constant[DOUBLE_WIDTH // 2] = (VALUE_A * VALUE_B) + 1
    }
    ```

!!! note

    Both Python (.py) and Packtype (.pt) syntaxes use Python's arithmetic and
    logical operators

## Oversized Values

When using explicitly sized constants, if a value is allocated to the constant
that is outside the legal range a `ValueError` will be raised:

=== "Python (.py)"

    ```python linenums="1"
    @packtype.package()
    class MyPackage:
        # Attempt to store 123 in a 4 bit value
        MY_CONSTANT : Constant[4] = 123
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        // Attempt to store 123 in a 4 bit value
        MY_CONSTANT : constant[4] = 123
    }
    ```

Will lead to:

```bash
ValueError: 123 is out of 4 bit range (0 to 15)
```
