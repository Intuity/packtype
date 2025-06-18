Type aliases allow one type to be referenced and renamed as another, which can
be used to create a localised reference to a foreign type.

## Example

The packtype definition:

```python linenums="1"
import packtype
from packtype import Alias, Scalar

@packtype.package()
class PackageA:
    TypeA : Scalar[5]

@packtype.package()
class PackageB:
    TypeB : Alias[PackageA.TypeA]
```

As rendered to SystemVerilog:

```sv linenums="1"
package package_a;
typedef logic [4:0] type_a_t;
endpackage : package_a

package package_b;
import package_a::type_a_t;
typedef type_a_t type_b_t;
endpackage : package_b
```

## Syntax

```python
@packtype.package()
class PackageB:
    # Format <NAME> : Alias[<TYPE_TO_ALIAS>]
    TypeB : Alias[PackageA.TypeA]
```
