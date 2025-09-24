    Descriptions can be added to packtype definitions as shown below.
The documentation is attached to the code in a way that will allow automated generation of documentation,
as with Python docstrings.

## Example

Descriptions can be added with normal [Python docstrings]((https://peps.python.org/pep-0257/)) or with the Packtype custom grammar:

=== "Python (.py)"

    ```python linenums="1"
    import packtype
    from packtype import Constant

    @packtype.package()
    class MyPackage:
        """
        Package decription,
        using normal Python docstrings
        """
        ...

    @MyPackage.enum()
    class Fruit:
        """
        Class description,
        using normal Python docstrings
        """
        APPLE  : Constant
        ORANGE : Constant
        PEAR   : Constant
        BANANA : Constant
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        """
        Package description
        using multiline docstring syntax
        """
        enum fruit_t {
            """
            Class description
            using multiline docstring syntax
            """
            @prefix=FRUIT
            APPLE  : constant
            "This is an apple"
            ORANGE : constant
            """
            Member descriptions can also be multiline.
            Use triple quotes for these.
            """
            PEAR   : constant
            "This is a pear"
            BANANA : constant
            "This is a banana"
        }

    }
    ```


```
