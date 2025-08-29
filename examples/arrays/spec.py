import packtype
from packtype import Constant, Scalar


@packtype.package()
class OneDimension:
    Scalar1D: Scalar[4]


@OneDimension.struct()
class Struct1D:
    field_a: Scalar[4][3][2]
    field_b: Scalar[2][3][4]


@OneDimension.enum()
class Enum1D:
    VAL_A: Constant
    VAL_B: Constant
    VAL_C: Constant


@OneDimension.union()
class Union1D:
    member_a: Struct1D[2][3]
    member_b: Scalar[4][12][2][3]


@packtype.package()
class TwoDimension:
    Scalar2D: OneDimension.Scalar1D[3]
    Enum2D: OneDimension.Enum1D[2]
    Struct2D: OneDimension.Struct1D[4]
    Union2D: OneDimension.Union1D[2]


@packtype.package()
class ThreeDimension:
    Scalar3D: TwoDimension.Scalar2D[2]
    Enum3D: TwoDimension.Enum2D[4]
    Struct3D: TwoDimension.Struct2D[5]
    Union3D: TwoDimension.Union2D[3]
