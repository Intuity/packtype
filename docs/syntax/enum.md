Enums are defined using the `@<PACKAGE>.enum()` decorator, which both processes
the entries contained within them and associates them to the [package](package.md).
Entries of an enum can be given explicit values or enumerated automatically with
various different value patterns. The width of an enum can be defined explicitly
or inferred from the largest value encoded within it.

## Example

The packtype definition:

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

## Decorator Options

The decorator accepts options that modify the enum declaration:

| Name     | Default               | Description                                |
|----------|-----------------------|--------------------------------------------|
| `mode`   | `EnumMode.INDEXED`    | Defines how inferred values are assigned   |
| `width`  | Inferred by max value | Specifies the bit-width of the enum type   |
| `prefix` | `None`                | Customise the prefix in rendered languages |

The `mode` parameter may be set to one of the following values:

 * `EnumMode.INDEXED` - values start from `0` and are chosen sequentially;
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

## Explicit Values

Values within an enumeration can be assigned explicit values, these may be 
interspersed with implicitly assigned values and the tool will adopt explicit
values and continue to enumerate from that point:

```python linenums="1"
import packtype
from packtype import Constant

@Types.enum(width=8)
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

## Helper Properties and Methods

Enum definitions expose a collection of helper functions for properties related
to the enumeration:

 * `<ENUM>._pt_width` - property that returns the bit width of the enumerated 
   values;
 * `<ENUM>._pt_mask` - property that returns a bit mask matched to the width of
   the enumerated value (i.e. `(1 << MyEnum._pt_width) - 1`);
 * `<ENUM>._pt_as_dict()`  - function that returns a dictionary of the values 
   of the enumeration with the key as the name as the value as the integer value;
