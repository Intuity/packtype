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

from collections.abc import Iterable
from copy import copy
from dataclasses import dataclass, field
from textwrap import dedent

from svg import SVG, Rect, Style, Text

from ..base import Base
from ..struct import Struct
from ..union import Union


@dataclass
class Point:
    x: int
    y: int


@dataclass
class SvgConfig:
    padding: Point = field(default_factory=lambda: Point(30, 30))
    name_font_size_px: int = 14
    bitnum_font_size_px: int = 12
    per_bit_width: int = 10
    cell_height: int = 30
    stroke_width: int = 3
    element_stroke: str = "black"
    element_fill: str = "transparent"


class SvgElement:
    def __init__(self, config: SvgConfig, instance: Base, name: str):
        self.config = config
        self.instance = instance
        self.name = name.strip()

    @property
    def width(self) -> int:
        return self.config.per_bit_width * self.instance._pt_width

    @property
    def height(self) -> int:
        return self.config.cell_height

    def render(self, position: Point | None = None) -> Iterable[Rect]:
        position = position or Point(0, 0)
        # Does the text need to be truncated?
        max_chars = self.width // (self.config.name_font_size_px // 2)
        if max_chars > 3 and max_chars < len(self.name):
            trunc_name = self.name[: max_chars - 3] + "..."
        else:
            trunc_name = self.name[:max_chars]
        # Estimate the text size
        est_text_width = len(trunc_name) * (self.config.name_font_size_px // 2)
        # Calculate center point of box
        center = Point(
            position.x + (self.width // 2),
            position.y + (self.height // 2) + self.config.stroke_width,
        )
        # Render the base rectangle
        yield Rect(
            x=position.x,
            y=position.y,
            width=self.width,
            height=self.height,
            stroke=self.config.element_stroke,
            stroke_width=self.config.stroke_width,
            fill=self.config.element_fill,
        )
        # Render the text
        yield Text(
            x=center.x - (est_text_width // 2),
            y=center.y,
            class_=["normal"],
            text=trunc_name,
        )
        # Bit numbering
        yield Text(
            x=position.x,
            y=position.y - self.config.bitnum_font_size_px,
            class_=["bitnum"],
            text="31",
        )
        yield Text(
            x=position.x + self.width - (1 * self.config.bitnum_font_size_px),
            y=position.y - self.config.bitnum_font_size_px,
            class_=["bitnum"],
            text="0",
        )
        # Bit width
        yield Text(
            x=center.x
            - (len(str(self.instance._pt_width)) * self.config.bitnum_font_size_px)
            // 2,
            y=position.y
            + self.config.cell_height
            + self.config.bitnum_font_size_px
            + self.config.stroke_width * 2,
            class_=["bitnum"],
            text=str(self.instance._pt_width),
        )


class SvgHierarchy:
    def __init__(self, config: SvgConfig, instance: Struct | Union) -> None:
        self.config = config
        self.instance = instance
        self.children: list[SvgHierarchy | SvgElement] = []

    @property
    def width(self) -> int:
        return sum(x.width for x in self.children)

    def attach(self, element: type["SvgHierarchy"] | SvgElement) -> None:
        self.children.append(element)

    def render(self, position: Point | None = None) -> Iterable[Rect]:
        position = copy(position) or Point(0, 0)
        for child in self.children:
            print(f"Rendering {type(child.instance).__name__} @ {position=}")
            yield from child.render(position)
            position.x += child.width


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
        def _recurse(instance: Struct | Union) -> SvgHierarchy:
            hier = SvgHierarchy(self.config, instance)
            for field, name in instance._pt_fields.items():
                if field._PT_BASE in (Struct, Union):
                    inner = _recurse(field)
                    hier.attach(inner)
                else:
                    hier.attach(SvgElement(self.config, field, name))
            return hier

        return _recurse(instance)

    def render(self) -> str:
        top_element = self._process(self.top())
        c_width = top_element.width + 2 * self.config.padding.x
        c_height = self.config.cell_height + 2 * self.config.padding.y
        elements = [
            Style(
                text=dedent(
                    f"""
                    .name {{ font: {self.config.name_font_size_px}px monospace; }}
                    .bitnum {{ font: {self.config.bitnum_font_size_px}px monospace; }}
                    """
                )
            ),
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
