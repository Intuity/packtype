Structs are defined using the `@<PACKAGE>.struct()` decorator, which processes
the definition and attaches it to the [package](package.md). Fields of a struct
may be declared as [scalars](scalar.md) or reference [enums](enum.md), other
structs, or [unions](union.md).

## Example

The packtype definition:

```python linenums="1"
import packtype
from packtype import Constant, Scalar

@packtype.package()
class MyPackage:
    INSTR_W : Constant = 32
    RegSel  : Scalar[5]

@MyPackage.enum(width=8)
class Opcode:
    ADD : Constant = 0
    SUB : Constant = 1
    ...

@MyPackage.struct(width=MyPackage.INSTR_W)
class Instruction:
    """Description of the struct can go here"""
    opcode : Opcode
    rd     : MyPackage.RegSel
    rs1    : MyPackage.RegSel
    rs2    : MyPackage.RegSel
    imm    : Scalar[9]
```

As rendered to SystemVerilog

```sv linenums="1"
package my_package;

// ...supporting declarations...

typedef struct packed {
    logic [8:0] imm;
    reg_sel_t rs2;
    reg_sel_t rs1;
    reg_sel_t rd;
    opcode_t opcode;
} instruction_t;

endpackage : my_package
```

## Decorator Options

The decorator accepts options that modify the struct declaration:

| Name      | Default               | Description                                |
|-----------|-----------------------|--------------------------------------------|
| `width`   | Inferred by fields    | Fixes the bit-width of the struct type     |
| `packing` | `Packing.FROM_LSB`    | Controls placement order of fields         |

The `width` parameter may be omitted, in which case it is inferred from the total
width of all fields contained within the struct. Where it is specified, a
`WidthError` will be raised if the total field width exceeds the specified `width`.
Where the total field width is less than the specified `width`, and automatic
`_padding` field will be added to the struct after all declared fields are placed.

The `packing` parameter may be set to one of two values:

 * `Packing.FROM_LSB` - fields are placed starting from the least significant bit
   of the struct (i.e. bit `0`);
 * `Packing.FROM_MSB` - fields are placed starting from the most significant bit
   of the struct (i.e. bit `WIDTH-1`).

!!! note

    The packing order does not affect the bit endianness of fields. Fields are
    _always_ declared as little bit endian.

## Helper Properties and Methods

Struct definitions expose a collection of helper functions for properties related
to the type:

 * `<STRUCT>._pt_width` - property that returns the bit width of the struct;
 * `<STRUCT>._pt_mask` - property that returns a bit mask matched to the width of
   the struct (i.e. `(1 << <STRUCT>._pt_width) - 1`);
 * `<STRUCT>._pt_fields` - property that returns a dictionary of fields within
   the struct with the key being the field instance and the value being the
   field's name;
 * `<STRUCT>._pt_field_width` - property that returns the total width of all
   fields in the structure, which may be less that or equal to the overall
   structure's width (as it ignores the `_padding` field);
 * `<STRUCT>._pt_fields_lsb_asc` - property that returns a list of tuples for
   each field of the struct starting from bit `0`, each tuple contains the LSB,
   MSB, and a nested tuple of name and instance;
 * `<STRUCT>._pt_fields_msb_desc` - property that returns a list of tuples for
   each field of the struct starting from bit `WIDTH-1`, each tuple contains the
   LSB, MSB, and a nested tuple of name and instance;
 * `<STRUCT>._pt_lsb(field: str)` - function that returns the LSB of a given
   field name;
 * `<STRUCT>._pt_msb(field: str)` - function that returns the MSB of a given
   field name;
 * `<STRUCT>._pt_pack()` - packs all values contained within the struct into a
   singular integer value (can also be achieved by casting to an int, e.g.
   `int(<STRUCT>)`);
 * `<STRUCT>._pt_unpack(packed: int)` - unpacks an integer value into the fields
   of the struct;
 * `<STRUCT>._pt_as_svg(cfg: SvgConfig)` - renders the struct as an SVG, see the
   section below for more details.

## Rendering to SVG

Struct definitions support both `__repr_svg__` and `_pt_as_svg` methods, the
former being defined as part of
[IPython's rich representation methods](https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display).

The `__repr_svg__` method will use the default style to generate an SVG
representation of the struct showing the field placements, while `_pt_as_svg`
allows an optional `SvgConfig` object to be passed which allows for customisation
of the rendering style (changing fonts, line widths, bit spacing, and more).

Images can be included in Mkdocs documentation using the plugin:

```md
!ptsvg[examples.structs.spec][Calendar.DateTime]
```

!ptsvg[examples.structs.spec][Calendar.DateTime]

The syntax is:

```md
!ptsvg[<PYTHON_MODULE_PATH>][<PACKAGE>.<STRUCT>]
```

You will need to add the following to your `mkdocs.yml`:

```yaml
...
markdown_extensions:
  ...
  - packtype.mkdocs.plugin
```
