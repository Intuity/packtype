Packtype is used to define constants and packed data structures using a syntax 
similar to Python [dataclasses](https://docs.python.org/3/library/dataclasses.html), 
these definitions can then be interrogated, rendered into various output formats,
or used natively in Python. The project originated from a need to sample and
drive structs and union ports on the boundary of SystemVerilog designs from 
cocotb in non-commercial simulators.

## Installation

The easiest way to install Packtype is to use PyPI:

```
$> python3 -m pip install packtype
```

Alternatively, you can install the development branch directly from the repository:

```
$> python3 -m pip install git+https://github.com/Intuity/packtype
```
