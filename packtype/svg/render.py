# Copyright 2023, Peter Birch, mailto:peter@intuity.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum, auto
from collections.abc import Iterable
from copy import copy
from dataclasses import dataclass, field
from textwrap import dedent

import svg
from svg import SVG, Line, Rect, Style, Text, TSpan, Path, Pattern


@dataclass
class Point:
    """A point position - (X, Y) coordinates"""
    x: int
    y: int


@dataclass
class LineStyle:
    """Defines the style for a line (width and stroke colour)"""
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
    """Defines a text style (font, size, and colour)"""
    font: str = "monospace"
    size: int = 12
    colour: str = "black"


@dataclass
class AlternationStyle:
    """Define the alternating colour style"""
    spacing: int = 4
    """How many bits should be in each background colour"""
    colours: tuple[str, str] = ("#FFF", "#EEE")
    """The set of background colours to alternate through"""


@dataclass
class AnnotationStyle:
    """Define the style for annotations"""
    style: TextStyle = field(default_factory=TextStyle)
    """Text style (font, size, colour)"""
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
    """Default background colour for fields"""
    box_style: LineStyle = field(default_factory=LineStyle)
    """Define the line style to use for the boxes around fields"""
    tick_style: LineStyle = field(default_factory=LineStyle)
    """Define the bit tick style to use within fields"""
    hatching: HatchStyle = field(default_factory=HatchStyle)
    """Define the hatching style to use for selected fields"""
    alternation: AlternationStyle = field(default_factory=AlternationStyle)
    """Define the background colour alternation style"""


class ElementStyle(Enum):
    """Style to use for an element"""
    NORMAL = auto()
    """Default background colour and clear overlay"""
    HATCHED = auto()
    """Hatched overlay"""
    BLOCKED = auto()
    """Block-out (black) overlay"""


class SvgElement:
    def __init__(self,
                 bit_width: int,
                 name: str,
                 msb: int,
                 style: ElementStyle = ElementStyle.NORMAL,
                 static_value: int | None = None,
                 config: SvgConfig | None = None):
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

    def _estimate_name_text(self, text: str) -> int:
        return len(text) * (self.config.name_style.size // 2)

    def _estimate_bit_text(self, text: str) -> int:
        return len(text) * (self.config.bit_style.size // 2)

    def render(self,
               position: Point | None = None,
               final: bool = False) -> Iterable[Rect]:
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
        # Background colour alternation
        if self.config.alternation.spacing > 0:
            for idx in range(self.bit_width):
                yield Rect(
                    x=position.x + idx * self.config.per_bit_width,
                    y=position.y,
                    width=self.config.per_bit_width,
                    height=self.config.cell_height,
                    fill=self.config.alternation.colours[
                        ((self.msb-idx) // self.config.alternation.spacing) %
                        len(self.config.alternation.colours)
                    ],
                )
        # Render the base rectangle
        points = [
            svg.M(position.x + self.px_width, position.y + self.px_height),
            svg.L(position.x, position.y + self.px_height),
            svg.L(position.x, position.y),
            svg.L(position.x + self.px_width, position.y),
        ]
        if final:
            points.append(svg.L(position.x + self.px_width, position.y + self.px_height),)
        yield Path(
            d=points,
            stroke=self.config.box_style.stroke,
            stroke_width=self.config.box_style.width,
            fill=self.config.element_fill,
        )
        # Render either the name or a static value
        if self.static_value is not None:
            for idx, bit in enumerate(f"{self.static_value:0{self.bit_width}b}"[:self.bit_width]):
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
                }[self.style]
            )


class SvgHierarchy:
    def __init__(self,
                 config: SvgConfig,
                 left_annotation: str | None = None,
                 right_annotation: str | None = None) -> None:
        self.config = config
        self.annotations = (left_annotation, right_annotation)
        self.children: list[SvgHierarchy | SvgElement] = []

    @property
    def px_width(self) -> int:
        return sum(x.px_width for x in self.children)

    @property
    def bit_width(self) -> int:
        return sum(x.bit_width for x in self.children)

    def attach(self, element: type["SvgHierarchy"] | SvgElement) -> None:
        self.children.append(element)

    def render(self,
               position: Point | None = None,
               final: bool = True) -> Iterable[Rect]:
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
        # Bit fields
        for idx, child in enumerate(self.children):
            yield from child.render(
                position,
                final=final and idx == (len(self.children) - 1),
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
                elements=[TSpan(text=x, x=right_x, dy="1em") for x in right.split("\n")]
            )


class SvgRender:
    def __init__(
        self,
        config: SvgConfig | None = None,
        left_annotation: str | None = None,
        right_annotation: str | None = None,
    ) -> None:
        self.config = config or SvgConfig()
        self.root = SvgHierarchy(
            self.config,
            left_annotation=left_annotation,
            right_annotation=right_annotation
        )

    def attach(self, element: SvgElement) -> None:
        element.config = self.config
        self.root.attach(element)

    def render(self) -> str:
        c_width = sum((
            self.root.px_width,
            2 * self.config.padding.x,
            self.config.left_annotation.width,
            self.config.left_annotation.padding,
            self.config.right_annotation.width,
            self.config.right_annotation.padding
        ))
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
                        font: {self.config.name_style.size}px sans-serif;
                        text-anchor: middle;
                    }}
                    .msb {{
                        font: {self.config.bit_style.size}px sans-serif;
                        text-anchor: start;
                    }}
                    .lsb {{
                        font: {self.config.bit_style.size}px sans-serif;
                        text-anchor: end;
                    }}
                    .width {{
                        font: {self.config.bit_style.size}px sans-serif;
                        text-anchor: middle;
                    }}
                    .left_annotation {{
                        font: {self.config.left_annotation.style.size}px sans-serif;
                        text-anchor: end;
                    }}
                    .right_annotation {{
                        font: {self.config.right_annotation.style.size}px sans-serif;
                        text-anchor: start;
                    }}
                    """
                )
            ),
            svg.Defs(elements=[
                Pattern(id="hatching",
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
                        ]
                        )
            ])
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
