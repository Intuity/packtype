Instances of types can be associated to a package, allowing structured constant
values to be declared.

## Example

The Packtype definition can either use a Python dataclass style or the Packtype
custom grammar:

=== "Python (.py)"

    ```python linenums="1"
    import packtype
    from packtype import Constant, Scalar

    @packtype.package()
    class MyPackage:
        pass

    @MyPackage.enum()
    class Month:
        JAN : Constant
        FEB : Constant
        ...
        DEC : Constant

    @MyPackage.struct()
    class Date:
        year  : Scalar[12]
        month : Month
        day   : Scalar[5]

    MyPackage._pt_attach_instance("SUMMER_START", Month.JUN)
    MyPackage._pt_attach_instance("SUMMER_END", Month.AUG)
    MyPackage._pt_attach_instance("CHRISTMAS", Date(year=2025, month=Month.DEC, day=25))
    ```

=== "Packtype (.pt)"

    ```sv linenums="1"
    package my_package {
        enum month_e {
            JAN : constant
            FEB : constant
            ...
            DEC : constant
        }

        struct date_t {
            year  : scalar[12]
            month : month_e
            day   : scalar[5]
        }

        SUMMER_START : month_e = month_e::JUN
        SUMMER_END   : month_e = month_e::AUG
        CHRISTMAS    : date_t  = {
            year  = 2025
            month = month_e::DEC
            day   = 25
        }
    }
    ```

As rendered to SystemVerilog:

```sv linenums="1"
package my_package;

localparam month_e SUMMER_START = month_e'(7);

localparam month_e SUMMER_END = month_e'(9);

// CHRISTMAS
localparam date_t CHRISTMAS = '{
      day: 5'h19
    , month: month_e'(11)
    , year: 12'h7E9
};

endpackage : my_package
```
