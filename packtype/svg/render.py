# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections.abc import Iterable
from copy import copy
from dataclasses import dataclass, field
from enum import Enum, auto
from textwrap import dedent

try:
    import svg
    from svg import SVG, Element, Line, Path, Pattern, Rect, Style, Text, TSpan
    SVG_RENDER_AVAILABLE = True
except ImportError as e:
    SVG_RENDER_AVAILABLE = False


class SvgRenderError(Exception):
    pass


@dataclass
class Size:
    """Size of an object (width, height)"""

    width: int
    height: int


@dataclass
class Point:
    """A point position - (X, Y) coordinates"""

    x: int
    y: int


@dataclass
class LineStyle:
    """Defines the style for a line (width and stroke color)"""

    width: int = 1
    stroke: str = "black"


@dataclass
class HatchStyle:
    """Defines the style for hatched areas"""

    spacing: int = 5
    width: int = 1
    stroke: str = "black"


@dataclass
class TextStyle:
    """Defines a text style (font, size, and color)"""

    font: str = "sans-serif"
    size: int = 12
    color: str = "black"

    def estimate(self, text: str) -> Size:
        """
        Estimate the width of text when rendered into the SVG, assuming that it
        is monospaced.

        :param text:  The text to render
        :returns:     Size (width, height) of the text
        """
        # NOTE: Many fonts have a width-height ratio of 3/5, this is why a fudge
        #       factor of 0.6 has been selected
        return Size(int((len(text) * self.size) * 0.6), self.size)


@dataclass
class AlternationStyle:
    """Define the alternating color style"""

    spacing: int = 4
    """How many bits should be in each background color"""
    colors: tuple[str, str] = ("#FFF", "#EEE")
    """The set of background colors to alternate through"""


@dataclass
class AnnotationStyle:
    """Define the style for annotations"""

    style: TextStyle = field(default_factory=TextStyle)
    """Text style (font, size, color)"""
    width: int = 0
    """Width of the annotation"""
    padding: int = 0
    """Padding between the annotation and the side of the bitfield"""


@dataclass
class SvgConfig:
    """Configure how the bitfield images are drawn"""

    padding: Point = field(default_factory=lambda: Point(30, 30))
    """Padding on the X and Y axis (applied on all 4 sides of the bitfield)"""
    left_annotation: AnnotationStyle = field(default_factory=AnnotationStyle)
    """Left-hand annotation style"""
    right_annotation: AnnotationStyle = field(default_factory=AnnotationStyle)
    """Right-hand annotation style"""
    name_style: TextStyle = field(default_factory=lambda: TextStyle(size=14))
    """Field name style"""
    bit_style: TextStyle = field(default_factory=lambda: TextStyle(size=12))
    """Bit number and width style"""
    per_bit_width: int = 20
    """Per-bit width to use to size fields"""
    cell_height: int = 40
    """Height to draw bitfields"""
    element_fill: str = "transparent"
    """Default background color for fields"""
    box_style: LineStyle = field(default_factory=LineStyle)
    """Define the line style to use for the boxes around fields"""
    tick_style: LineStyle = field(default_factory=LineStyle)
    """Define the bit tick style to use within fields"""
    hatching: HatchStyle = field(default_factory=HatchStyle)
    """Define the hatching style to use for selected fields"""
    alternation: AlternationStyle = field(default_factory=AlternationStyle)
    """Define the background color alternation style"""


class ElementStyle(Enum):
    """Style to use for an element"""

    NORMAL = auto()
    """Default background color and clear overlay"""
    HATCHED = auto()
    """Hatched overlay"""
    BLOCKED = auto()
    """Block-out (black) overlay"""


class SvgField:
    """
    SVG representation of a single bit field within a structure

    :param bit_width:    Width of the field in bits
    :param name:         ASCII name of the field
    :param msb:          Most significant bit (fields placed left-to-right)
    :param style:        Style to render the field (NORMAL, HATCHED, BLOCKED)
    :param static_value: Static bit-wise value to encode in the field, this will
                         take the place of the name
    :param config:       Style configuration
    """

    def __init__(
        self,
        bit_width: int,
        name: str,
        msb: int,
        style: ElementStyle = ElementStyle.NORMAL,
        static_value: int | None = None,
        config: SvgConfig | None = None,
    ):
        self.bit_width = bit_width
        self.name = name.strip()
        self.msb = msb
        self.style = style
        self.static_value = static_value
        self.config = config

    @property
    def lsb(self) -> int:
        return self.msb - self.bit_width + 1

    @property
    def px_width(self) -> int:
        return self.config.per_bit_width * self.bit_width

    @property
    def px_height(self) -> int:
        return self.config.cell_height

    def render(
        self, position: Point | None = None, final: bool = False
    ) -> Iterable[Element]:
        """
        Render the bit field from a starting position.

        :param position: The top-left coordinate to draw from
        :param final:    Whether this field is the last to be rendered, in which
                         case the right-hand wall will be added
        :yields:         A series of SVG elements
        """
        position = position or Point(0, 0)
        # Does the text need to be truncated?
        max_chars = self.px_width // (self.config.name_style.size // 2)
        if max_chars > 3 and max_chars < len(self.name):
            trunc_name = self.name[: max_chars - 3] + "..."
        else:
            trunc_name = self.name[:max_chars]
        # Calculate center point of box
        box_center = Point(
            position.x + (self.px_width // 2),
            position.y + (self.px_height // 2),
        )
        # Background color alternation
        if self.config.alternation.spacing > 0:
            for idx in range(self.bit_width):
                yield Rect(
                    x=position.x + idx * self.config.per_bit_width,
                    y=position.y,
                    width=self.config.per_bit_width,
                    height=self.config.cell_height,
                    fill=self.config.alternation.colors[
                        ((self.msb - idx) // self.config.alternation.spacing)
                        % len(self.config.alternation.colors)
                    ],
                )
        # Render the base rectangle (open ended if not the final field)
        points = [
            svg.M(position.x + self.px_width, position.y + self.px_height),
            svg.L(position.x, position.y + self.px_height),
            svg.L(position.x, position.y),
            svg.L(position.x + self.px_width, position.y),
        ]
        if final:
            points.append(
                svg.L(position.x + self.px_width, position.y + self.px_height),
            )
        yield Path(
            d=points,
            stroke=self.config.box_style.stroke,
            stroke_width=self.config.box_style.width,
            fill=self.config.element_fill,
        )
        # Render either the name or a static value
        if self.static_value is not None:
            for idx, bit in enumerate(
                f"{self.static_value:0{self.bit_width}b}"[: self.bit_width]
            ):
                bit_center = int(position.x + (idx + 0.5) * self.config.per_bit_width)
                yield Text(
                    x=bit_center,
                    y=box_center.y,
                    class_=["baseline", "name"],
                    text=bit,
                )
        else:
            yield Text(
                x=box_center.x,
                y=box_center.y,
                class_=["baseline", "name"],
                text=trunc_name,
            )
        # Bit numbering
        msb_txt = str(self.msb)
        lsb_txt = str(self.lsb)
        yield Text(
            x=position.x + self.config.name_style.size // 4,
            y=position.y - self.config.bit_style.size,
            class_=["baseline", "msb"],
            text=msb_txt,
        )
        yield Text(
            x=position.x + self.px_width - self.config.name_style.size // 4,
            y=position.y - self.config.bit_style.size,
            class_=["baseline", "lsb"],
            text=lsb_txt,
        )
        # Bit width
        yield Text(
            x=box_center.x,
            y=position.y
            + self.config.cell_height
            + self.config.bit_style.size
            + self.config.box_style.width * 2,
            class_=["baseline", "width"],
            text=str(self.bit_width),
        )
        # Bit ticks
        for idx in range(1, self.bit_width):
            yield Line(
                x1=position.x + idx * self.config.per_bit_width,
                y1=position.y,
                x2=position.x + idx * self.config.per_bit_width,
                y2=position.y + 5,
                stroke=self.config.tick_style.stroke,
                stroke_width=self.config.tick_style.width,
            )
            yield Line(
                x1=position.x + idx * self.config.per_bit_width,
                y1=position.y + self.config.cell_height - 5,
                x2=position.x + idx * self.config.per_bit_width,
                y2=position.y + self.config.cell_height,
                stroke=self.config.tick_style.stroke,
                stroke_width=self.config.tick_style.width,
            )
        # If reserved, strike through
        if self.style in (ElementStyle.HATCHED, ElementStyle.BLOCKED):
            yield Rect(
                x=position.x,
                y=position.y,
                width=self.px_width,
                height=self.px_height,
                fill={
                    ElementStyle.HATCHED: "url(#hatching)",
                    ElementStyle.BLOCKED: "black",
                }[self.style],
            )


class SvgBitFields:
    """
    Holds a collection of fields and manages the rendering operation.

    :param config:           Style configuration
    :param left_annotation:  Text to place on the left of the rendered fields
    :param right_annotation: Text to place on the right of the rendered fields
    """

    def __init__(
        self,
        config: SvgConfig,
        left_annotation: str | None = None,
        right_annotation: str | None = None,
    ) -> None:
        self.config = config
        self.annotations = (left_annotation, right_annotation)
        self.children: list[SvgField] = []

    @property
    def px_width(self) -> int:
        return sum(x.px_width for x in self.children)

    @property
    def bit_width(self) -> int:
        return sum(x.bit_width for x in self.children)

    def attach(self, element: SvgField) -> None:
        assert isinstance(element, SvgField)
        self.children.append(element)

    def render(self, position: Point | None = None) -> Iterable[Element]:
        """
        Render the collection of bitfields from a given starting position.

        :param position: Position to render the bit fields
        :yields:         A series of SVG elements
        """
        position = copy(position) or Point(0, 0)
        left, right = self.annotations
        # Left annotation
        if left is not None:
            yield Text(
                x=position.x + self.config.left_annotation.width,
                y=position.y + self.config.cell_height // 2,
                class_=["baseline", "left_annotation"],
                text=left,
            )
            position.x += self.config.left_annotation.width
            position.x += self.config.left_annotation.padding
        # Bit fields (rendering left-to-right, MSB-to-LSB)
        for idx, child in enumerate(
            sorted(self.children, key=lambda x: x.msb, reverse=True)
        ):
            yield from child.render(
                position,
                final=(idx == (len(self.children) - 1)),
            )
            position.x += child.px_width
        # Right annotation
        if right:
            right_x = position.x + self.config.right_annotation.padding
            yield Text(
                x=right_x,
                y=position.y,
                class_=["right_annotation"],
                overflow="visible",
                elements=[
                    TSpan(text=x, x=right_x, dy="1em") for x in right.split("\n")
                ],
            )


class SvgRender:
    """
    Class for managing the rendering of an SVG bitfield, applying overall text
    styles and setting up the canvas.

    :param config:           Style configuration
    :param left_annotation:  Text to place on the left of the bit field
    :param right_annotation: Text to place on the right of the bit field
    """

    def __init__(
        self,
        config: SvgConfig | None = None,
        left_annotation: str | None = None,
        right_annotation: str | None = None,
    ) -> None:
        global SVG_RENDER_AVAILABLE
        if not SVG_RENDER_AVAILABLE:
            raise SvgRenderError(
                "SVG rendering is not available, please install the svg package."
            )
        self.config = config or SvgConfig()
        self.root = SvgBitFields(
            self.config,
            left_annotation=left_annotation,
            right_annotation=right_annotation,
        )

    def attach(self, element: SvgField) -> None:
        """
        Attach a new SVG field into the collection of bit fields.

        :param element: The element to append
        """
        element.config = self.config
        self.root.attach(element)

    def render(self) -> str:
        """
        Render the bit fields into an SVG relying on the child bit fields.

        :returns: Rendered string of the SVG
        """
        c_width = sum(
            (
                self.root.px_width,
                2 * self.config.padding.x,
                self.config.left_annotation.width,
                self.config.left_annotation.padding,
                self.config.right_annotation.width,
                self.config.right_annotation.padding,
            )
        )
        c_height = self.config.cell_height + 2 * self.config.padding.y
        elements = [
            Style(
                text=dedent(
                    f"""
                    .baseline {{
                        white-space: pre-line;
                        dominant-baseline: central;
                    }}
                    .name {{
                        font-size: {self.config.name_style.size}px;
                        font-family: {self.config.name_style.font};
                        color: {self.config.name_style.color};
                        text-anchor: middle;
                    }}
                    .msb {{
                        font-size: {self.config.bit_style.size}px;
                        font-family: {self.config.bit_style.font};
                        color: {self.config.bit_style.color};
                        text-anchor: start;
                    }}
                    .lsb {{
                        font-size: {self.config.bit_style.size}px;
                        font-family: {self.config.bit_style.font};
                        color: {self.config.bit_style.color};
                        text-anchor: end;
                    }}
                    .width {{
                        font-size: {self.config.bit_style.size}px;
                        font-family: {self.config.bit_style.font};
                        color: {self.config.bit_style.color};
                        text-anchor: middle;
                    }}
                    .left_annotation {{
                        font-size: {self.config.left_annotation.style.size}px;
                        font-family: {self.config.left_annotation.style.font};
                        color: {self.config.left_annotation.style.color};
                        text-anchor: end;
                    }}
                    .right_annotation {{
                        font-size: {self.config.right_annotation.style.size}px
                        font-family: {self.config.right_annotation.style.font};
                        color: {self.config.right_annotation.style.color};
                        text-anchor: start;
                    }}
                    """
                )
            ),
            svg.Defs(
                elements=[
                    Pattern(
                        id="hatching",
                        width=self.config.hatching.spacing,
                        height=self.config.hatching.spacing,
                        patternTransform="rotate(45 0 0)",
                        patternUnits="userSpaceOnUse",
                        elements=[
                            svg.Line(
                                x1=0,
                                y1=0,
                                x2=0,
                                y2=self.config.hatching.spacing,
                                stroke=self.config.hatching.stroke,
                                stroke_width=self.config.hatching.width,
                            )
                        ],
                    )
                ]
            ),
        ]
        elements += list(
            self.root.render(Point(self.config.padding.x, self.config.padding.y))
        )
        return str(
            SVG(
                width=c_width,
                height=c_height,
                elements=elements,
            )
        )
