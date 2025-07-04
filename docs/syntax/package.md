Packages separate [aliases](alias.md), [constants](constant.md),
[enumerations](enum.md), [structs](struct.md), and [unions](union.md) into
distinct namespaces - definitions cannot otherwise exist outside of a package.

## Example

The Packtype definition can either use a Python dataclass style or the Packtype
custom grammar:

=== "Python (.py)"

    ```python linenums="1"
    import packtype

    @packtype.package()
    class MyPackage:
        """Description of what purpose this package serves"""
        ...
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        "Description of what purpose this package serves"
        // ...
    }
    ```

As rendered to SystemVerilog:

```sv linenums="1"
package my_package;

// ...attached definitions...

endpackage : my_package
```

## Imports

Types and constants defined in one package may reference types and constants
defined in another package and Packtype will track which entities are local and
foreign.

=== "Python (.py)"

    When using the Python dataclass style syntax, packages may be referenced in
    the same fashion that normal imports operate:

    ```python title="package_a.py" linenums="1"
    import packtype
    from packtype import Constant

    @packtype.package()
    class PackageA:
        VALUE_A : Constant[8] = 0x12
    ```

    ```python title="package_b.py" linenums="1"
    import packtype
    from packtype import Constant

    from package_a import PackageA

    @packtype.package()
    class PackageB:
        VALUE_B : Constant[8] = PackageA.VALUE_A + 3
    ```

=== "Packtype (.pt)"

    When using the Packtype custom grammar, packages may be referenced using the
    `import` keyword:

    ```sv title="package_a.pt" linenums="1"
    package package_a {
        VALUE_A : constant[8] = 0x12
    }
    ```

    ```sv title="package_b.pt" linenums="1"
    package package_b {
        import package_a::VALUE_A
        VALUE_B : constant[8] = VALUE_A + 3
    }
    ```

    !!! note

        When using the Packtype custom grammar, all packages that are referenced
        will need to be provided to Packtype in order for imports to be resolved

## Python Decorators

Python package definitions expose a set of decorators for declaring attached types:

 * `@<PACKAGE>.enum()` - used for declaring [enumerations](enum.md)
 * `@<PACKAGE>.struct()` - used for declaring packed [data structures](struct.md)
 * `@<PACKAGE>.union()` - used for declaring packed [unions](union.md)

## Helper Properties and Methods

Package definitions expose a collection of helper functions for accessing members
of the package:

 * `<PACKAGE>._pt_foreign()` - function returning the ordered set of types
   referenced by other packages in fields of [structs](struct.md) or
   [unions](union.md);
 * `<PACKAGE>._pt_fields` - property that returns the dictionary of definitions
   attached to the package where key is the field instance, value is the field
   name;
 * `<PACKAGE>._pt_constants` - property that returns an iterable of all
   [constants](constant.md) attached to the package, with each entry being a
   tuple of name and instance;
 * `<PACKAGE>._pt_scalars` - property that returns an iterable of all
   [scalars](scalar.md) attached to the package, with each entry being a tuple
   of name and instance;
 * `<PACKAGE>._pt_aliases` - property that returns an iterable of all type
   [aliases](alias.md) attached to the package, with each entry being a tuple of
   name and instance;
 * `<PACKAGE>._pt_enums` - property that returns an iterable of all
   [enumerations](enum.md) attached to the package, with each entry being a
   tuple of name and instance;
 * `<PACKAGE>._pt_structs` - property that returns an iterable of all
   [structs](struct.md) attached to the package, with each entry being a tuple of
   name and instance;
 * `<PACKAGE>._pt_unions` - property that returns an iterable of all
   [unions](union.md) attached to the package, with each entry being a tuple of
   name and instance;
 * `<PACKAGE>._pt_structs_and_unions` - property that returns an iterable of all
   [structs](struct.md) and [unions](union.md) attached to the package
   maintaining their order of declaration, with each entry being a tuple of name
   and instance;
 * `<PACKAGE>._pt_lookup()` - function that returns the name of a package field
   given its instance.
