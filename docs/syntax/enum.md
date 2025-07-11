Enums are defined using the `@<PACKAGE>.enum()` decorator or `enum` keyword.
Entries of an enum can be given explicit values or enumerated automatically with
various different value patterns. The width of an enum can be defined explicitly
or inferred from the largest value encoded within it.

## Example

The Packtype definition can either use a Python dataclass style or the Packtype
custom grammar:

=== "Python (.py)"

    ```python linenums="1"
    import packtype
    from packtype import Constant

    @packtype.package()
    class MyPackage:
        ...

    @MyPackage.enum()
    class Fruit:
        """Description of the enumeration can go here"""
        APPLE  : Constant
        ORANGE : Constant
        PEAR   : Constant
        BANANA : Constant
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        enum fruit_t {
            "Description of the enumeration can go here"
            @prefix=FRUIT
            APPLE  : constant
            ORANGE : constant
            PEAR   : constant
            BANANA : constant
        }
    }
    ```

As rendered to SystemVerilog:

```sv linenums="1"
package my_package;

typedef enum logic [1:0] {
    FRUIT_APPLE,
    FRUIT_ORANGE,
    FRUIT_PEAR,
    FRUIT_BANANA
} fruit_t;

endpackage : my_package
```


## Declaration Options

=== "Python (.py)"

    The decorator accepts options that modify the enum declaration:

    | Name     | Default               | Description                                |
    |----------|-----------------------|--------------------------------------------|
    | `mode`   | `EnumMode.INDEXED`    | Defines how inferred values are assigned   |
    | `width`  | Inferred by max value | Specifies the bit-width of the enum type   |
    | `prefix` | `None`                | Customise the prefix in rendered languages |

    The `mode` parameter may be set to one of the following values:

      * `EnumMode.INDEXED` - values start from `0` and are chosen sequentially (default);
      * `EnumMode.ONE_HOT` - values start from `1` and are chosen to have exactly one
        active bit (i.e powers of 2) so follow the sequence `1`, `2`, `4`, `8`, ...;
      * `EnumMode.GRAY` - values start from `0` and are assigned following a Gray
        code (only one bit changes between sequentially assigned values), an
        `EnumError` will be raised where not enough named constants are declared to
        fill the Gray code sequence.

    The `width` parameter may be omitted, in which case it is automatically inferred
    as the ceiling log2 of the maximum enumerated value. Where it is specified, an
    `EnumError` will be raised if the maximum enumerated value exceeds what can be
    expressed within the enum's bit width.

    The `prefix` may be used when rendering to languages that do not support name
    spacing of enumerated types - for example in SystemVerilog the names of the
    enumerated values will be `<PREFIX>_<VALUE_NAME>`. If omitted, the prefix will
    be inferred as the shouty snake case version of the enumeration's name.

=== "Packtype (.pt)"

    The `enum` declaration accepts options that modify the enum declaration,
    the full syntax is as follows:

    ```sv linenums="1"
    enum <MODE> [<WIDTH>] <NAME> {
        "<DESCRIPTION>"
        @<MODIFIER_KEY>=@<MODIFIER_VALUE>
        ...
    }
    ```

    For example:

    ```sv linenums="1"
    enum onehot [8] my_onehot_enum_t {
        "My wonderful enum"
        @prefix=MYONE
        A
        B
        ...
    }
    ```

    The `<MODE>` option may omitted or set to one of the follow values:

      * `indexed` - values start from `0` and are chosen sequentially (default);
      * `onehot` - values start from `1` and are chosen to have exactly one
        active bit (i.e powers of 2) so follow the sequence `1`, `2`, `4`, `8`, ...;
      * `gray` - values start from `0` and are assigned following a Gray
        code (only one bit changes between sequentially assigned values), an
        `EnumError` will be raised where not enough named constants are declared to
        fill the Gray code sequence.

    The `<WIDTH>` parameter may be omitted, in which case it is automatically inferred
    as the ceiling log2 of the maximum enumerated value. Where it is specified, an
    `EnumError` will be raised if the maximum enumerated value exceeds what can be
    expressed within the enum's bit width.

    The `<MODIFIER>` syntax allows standard behaviours of Packtype to be altered,
    in the Python syntax these are given as keyword arguments to the decorator:

     * `@prefix=...` may be used when rendering to languages that do not support
       name spacing of enumerated types - for example in SystemVerilog the names
       of the enumerated values will be `<PREFIX>_<VALUE_NAME>`. If omitted, the
       prefix will be inferred as the shouty snake case version of the enumeration's
       name (.e.g entry `A` of `my_onehot_enum_t` will become `MY_ONEHOT_ENUM_T_A`).

## Explicit Values

Values within an enumeration can be assigned explicit values, these may be
interspersed with implicitly assigned values and the tool will adopt explicit
values and continue to enumerate from that point:

=== "Python (.py)"

    ```python linenums="1"
    import packtype
    from packtype import Constant

    @MyPackage.enum(width=8)
    class Opcodes:
        ALU_ADD : Constant = 0x10
        ALU_SUB : Constant # Infers 0x11
        ALU_MUL : Constant # Infers 0x12
        LDST_LB : Constant = 0x20
        LDST_LH : Constant # Infers 0x21
        LDST_LW : Constant # Infers 0x22
        LDST_SB : Constant = 0x30
        LDST_SH : Constant # Infers 0x31
        LDST_SW : Constant # Infers 0x32
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        enum [8] opcodes_t {
          ALU_ADD : constant = 0x10
          ALU_SUB : constant // Infers 0x11
          ALU_MUL : constant // Infers 0x12
          LDST_LB : constant = 0x20
          LDST_LH : constant // Infers 0x21
          LDST_LW : constant // Infers 0x22
          LDST_SB : constant = 0x30
          LDST_SH : constant // Infers 0x31
          LDST_SW : constant // Infers 0x32
        }
    }
    ```

## Helper Properties and Methods

Enum definitions expose a collection of helper functions for properties related
to the enumeration:

 * `<ENUM>._pt_width` - property that returns the bit width of the enumerated
   values;
 * `<ENUM>._pt_mask` - property that returns a bit mask matched to the width of
   the enumerated value (i.e. `(1 << MyEnum._pt_width) - 1`);
 * `<ENUM>._pt_as_dict()`  - function that returns a dictionary of the values
   of the enumeration with the key as the name as the value as the integer value;
