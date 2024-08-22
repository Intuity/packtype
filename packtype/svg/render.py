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
from svg import SVG, Line, Rect, Style, Text, Path, Pattern

from ..base import Base
from ..struct import Struct
from ..union import Union


@dataclass
class Point:
    x: int
    y: int


@dataclass
class LineStyle:
    width: int = 1
    stroke: str = "black"


@dataclass
class HatchStyle:
    spacing: int = 5
    width: int = 1
    stroke: str = "black"


@dataclass
class TextStyle:
    size: int = 12
    font: str = "monospace"
    colour: str = "black"


@dataclass
class SvgConfig:
    padding: Point = field(default_factory=lambda: Point(30, 30))
    name_style: TextStyle = field(default_factory=lambda: TextStyle(size=14))
    bit_style: TextStyle = field(default_factory=lambda: TextStyle(size=12))
    per_bit_width: int = 20
    cell_height: int = 40
    element_fill: str = "transparent"
    box_style: LineStyle = field(default_factory=LineStyle)
    tick_style: LineStyle = field(default_factory=LineStyle)
    hatching: HatchStyle = field(default_factory=HatchStyle)


class ElementStyle(Enum):
    NORMAL = auto()
    HATCHED = auto()
    BLOCKED = auto()


class SvgElement:
    def __init__(self,
                 config: SvgConfig,
                 instance: Base,
                 name: str,
                 msb: int,
                 style: ElementStyle = ElementStyle.NORMAL):
        self.config = config
        self.instance = instance
        self.name = name.strip()
        self.msb = msb
        self.style = style

    @property
    def bit_width(self) -> int:
        return self.instance._pt_width

    @property
    def lsb(self) -> int:
        return self.msb - self.bit_width + 1

    @property
    def px_width(self) -> int:
        return self.config.per_bit_width * self.instance._pt_width

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
        center = Point(
            position.x + (self.px_width // 2),
            position.y + (self.px_height // 2),
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
        # Render the text
        yield Text(
            x=center.x,
            y=center.y,
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
            x=center.x,
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
    def __init__(self, config: SvgConfig, instance: Struct | Union) -> None:
        self.config = config
        self.instance = instance
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
        for idx, child in enumerate(self.children):
            print(f"Rendering {type(child.instance).__name__} @ {position=}")
            yield from child.render(
                position,
                final=final and idx == (len(self.children) - 1),
            )
            position.x += child.px_width


class SvgRender:
    def __init__(
        self,
        top: type[Struct] | type[Union],
        canvas: tuple[int, int],
        config: SvgConfig | None = None,
    ) -> None:
        self.top = top
        self.canvas = canvas
        self.config = config or SvgConfig()

    def _process(self, instance: Struct | Union):
        def _recurse(instance: Struct | Union, msb: int | None = None) -> SvgHierarchy:
            hier = SvgHierarchy(self.config, instance)
            if msb is None:
                msb = instance._PT_WIDTH - 1
            for name, _ in sorted(
                ((name, lsb) for name, (lsb, _msb) in instance._PT_RANGES.items()),
                key=lambda x: x[1],
                reverse=True,
            ):
                field = getattr(instance, name)
                if field._PT_BASE in (Struct, Union):
                    inner = _recurse(field, msb=msb)
                else:
                    inner = SvgElement(
                        self.config,
                        field,
                        name,
                        msb,
                        style=ElementStyle.NORMAL,
                    )
                msb -= inner.bit_width
                hier.attach(inner)
            return hier

        return _recurse(instance)

    def render(self) -> str:
        top_element = self._process(self.top())
        c_width = top_element.px_width + 2 * self.config.padding.x
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
            top_element.render(Point(self.config.padding.x, self.config.padding.y))
        )
        return str(
            SVG(
                width=c_width,
                height=c_height,
                elements=elements,
            )
        )
