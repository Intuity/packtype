# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import base64
import importlib
import re
from xml.etree import ElementTree

from packtype.package import Package
from packtype.wrap import Registry

try:
    from markdown.extensions import Extension
    from markdown.inlinepatterns import InlineProcessor
except ImportError:

    class InlineProcessor:
        pass

    class Extension:
        pass


class PacktypeProcessor(InlineProcessor):
    RGX_BLOCK = r"!ptsvg\[([\w.]+)\]\[([\w.]+)\]"

    def handleMatch(  # noqa: N802
        self, match: re.Match, context: ElementTree.Element
    ) -> tuple[ElementTree.Element, int, int]:
        py_path, struct_path = match.groups()
        importlib.import_module(py_path)
        pkg_name, struct_name = struct_path.split(".")
        pkgs = Registry.query(Package)
        found = [x for x in pkgs if x.__name__ == pkg_name]
        if not found:
            raise KeyError(f"Package '{pkg_name}' not found in registry.")
        pkg = found[0]
        struct = getattr(pkg, struct_name, None)
        if not struct:
            raise KeyError(f"Struct '{struct_name}' not found in package '{pkg_name}'.")
        svg_b64 = base64.b64encode(struct()._pt_as_svg().encode("utf-8")).decode("utf-8")
        img = ElementTree.Element("img")
        img.set("src", f"data:image/svg+xml;base64,{svg_b64}")
        return img, match.start(0), match.end(0)


class PacktypeExtension(Extension):
    def extendMarkdown(self, md):  # noqa: N802
        md.inlinePatterns.register(
            PacktypeProcessor(
                pattern=PacktypeProcessor.RGX_BLOCK,
                md=md,
            ),
            "ptsvg",
            500,
        )


def makeExtension(**kwargs):  # noqa: N802
    return PacktypeExtension(**kwargs)
