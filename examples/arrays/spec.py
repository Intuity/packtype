import packtype
from packtype import Constant, Scalar


@packtype.package()
class OneDimension:
    Scalar1D : Scalar[4]

@OneDimension.struct()
class Struct1D:
    field_a : Scalar[3]
    field_b : Scalar[2]

@OneDimension.enum()
class Enum1D:
    VAL_A : Constant
    VAL_B : Constant
    VAL_C : Constant

@packtype.package()
class TwoDimension:
    Scalar2D : OneDimension.Scalar1D[3]
    Enum2D : OneDimension.Enum1D[2]
    Struct2D : OneDimension.Struct1D[4]

@packtype.package()
class ThreeDimension:
    Scalar3D : TwoDimension.Scalar2D[2]
    Enum3D : TwoDimension.Enum2D[4]
    Struct3D : TwoDimension.Struct2D[5]

me = ThreeDimension.Scalar3D()
