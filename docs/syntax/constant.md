Constants are defined using the `Constant` type and are declared directly within
the [package](package.md). They carry a fixed value, which may be computed from
other constants, and may be given an explicit bit width.

## Example

The packtype definition:

```python linenums="1"
import packtype
from packtype import Constant

@packtype.package()
class MyPackage:
    VALUE_A : Constant = 123
    VALUE_B : Constant[16] = 234
```

As rendered to SystemVerilog:

```sv linenums="1"
package my_package;

localparam VALUE_A = 123;
localparam bit [7:0] VALUE_B = 234;

endpackage : my_package
```

## Syntax

### Unsized Constants

A constant defined without an explicit size will be treated as unsized and it 
will be left to the target language template to decide what size container to
allocate it.

```python
@packtype.package()
class MyPackage:
    # Format: <NAME> : Constant = <VALUE>
    MY_CONSTANT : Constant = 123
```

### Implicit Constants

Unsized constants may be declared implicitly by omitting the `: Constant` keyword
from the declaration:

```python
@packtype.package()
class MyPackage:
    # Format: <NAME> = <VALUE>
    MY_CONSTANT = 123
```

### Sized Constants

Constants may be defined with an explicit bit width, in which case Packtype will
respect the request bit width internally and target language templates will 
allocate the nearest possible size large enough to hold the full range of that
number of bits.

```python
@packtype.package()
class MyPackage:
    # Format: <NAME> : Constant[<WIDTH>] = <VALUE>
    MY_CONSTANT : Constant[8] = 123
```

## Oversized Values

When using explicitly sized constants, if a value is allocated to the constant
that is outside the legal range a `ValueError` will be raised:

```python
@packtype.package()
class MyPackage:
    # Attempt to store 123 in a 4 bit value
    MY_CONSTANT : Constant[4] = 123
```

Will lead to:

```bash
ValueError: 123 is out of 4 bit range (0 to 15)
```
