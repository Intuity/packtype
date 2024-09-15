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

import importlib.util
import logging
import traceback
from pathlib import Path
from types import SimpleNamespace

import click
from mako import exceptions
from mako.lookup import TemplateLookup
from rich.logging import RichHandler
from rich.traceback import install

from .alias import Alias
from .array import PackedArray
from .assembly import Packing
from .base import Base
from .enum import Enum
from .package import Package
from .primitive import NumericPrimitive
from .registers import Behaviour, File, Register
from .scalar import Scalar
from .struct import Struct
from .svg.render import ElementStyle, SvgConfig, SvgField, SvgRender
from .templates.common import snake_case
from .union import Union
from .wrap import Registry

# Setup logging
logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("packtype")
log.setLevel(logging.INFO)

# Setup exception handling
install()


def resolve_to_object(
    baseline: list[Package],
    *path: str,
    acceptable: tuple[type[Base]] | None = None,
) -> Base:
    # Resolve to an object
    resolved = None
    for segment in path:
        if resolved is None:
            matched = [x for x in baseline if x.__name__ == segment]
            if len(matched) != 1:
                raise Exception(f"Cannot resolve baseline '{segment}'")
            resolved = matched[0]
        else:
            if (nxt_rslv := getattr(resolved, segment, None)) is None:
                raise Exception(
                    f"Cannot resolve '{segment}' within '{resolved.__name__}'"
                )
            resolved = nxt_rslv
    # Check the type is acceptable
    if not hasattr(resolved, "_PT_BASE"):
        raise Exception(f"Selection {path} resolved to a non-Packtype object")
    elif acceptable is not None and not issubclass(resolved, acceptable):
        raise Exception(
            f"Selection {path} resolved to an object of type "
            f"{resolved._PT_BASE.__name__} which cannot be rendered as an SVG"
        )
    return resolved


# Handle CLI
@click.group()
@click.option("--debug", flag_value=True, default=False, help="Enable debug messages")
@click.argument("spec", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def main(ctx, debug: bool, spec: str):
    """Renders packtype definitions into different forms"""
    ctx.ensure_object(dict)
    # Set log verbosity
    if debug:
        log.setLevel(logging.DEBUG)
    # Convert spec and outdir to pathlib objects
    log.debug(f"Using specification: {spec.absolute()}")
    # Import library
    imp_spec = importlib.util.spec_from_file_location(spec.stem, spec.absolute())
    imp_spec.loader.exec_module(importlib.util.module_from_spec(imp_spec))
    # Query the registry for packages
    baseline = list(Registry.query(Package)) + list(Registry.query(File))
    log.debug(f"Discovered {len(baseline)} baseline definitions")
    # Attach packages to context
    ctx.obj["baseline"] = baseline


@main.command()
@click.pass_context
def inspect(ctx):
    baseline = SimpleNamespace(**{x.__name__: x for x in ctx.obj.get("baseline", [])})
    log.warning("Use the 'baseline' namespace to inspect Packtype definitions")
    breakpoint()
    del baseline


@main.command()
@click.argument("selection", type=str)
@click.argument(
    "output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    required=False,
)
@click.pass_context
def svg(ctx, selection: str, output: Path | None):
    # Resolve selection to a struct or union
    resolved = resolve_to_object(
        ctx.obj.get("baseline", []),
        *selection.split("."),
        acceptable=(Struct, Union),
    )

    # Create a rendering instance
    cfg = SvgConfig()
    cfg.left_annotation.width = cfg.left_annotation.style.estimate(
        resolved.__name__
    ).width
    cfg.left_annotation.padding = 10
    svg = SvgRender(cfg, left_annotation=resolved.__name__)

    # Recurse through the object to construct the SVG hierarchy
    def _recurse(instance: Struct | Union, msb: int | None = None):
        nonlocal svg
        if msb is None:
            msb = instance._PT_WIDTH - 1
        for name, _lsb in sorted(
            ((name, lsb) for name, (lsb, _msb) in instance._PT_RANGES.items()),
            key=lambda x: x[1],
            reverse=True,
        ):
            field = getattr(instance, name)
            if field._PT_BASE in (Struct, Union):
                _recurse(field, msb=msb)
            else:
                svg.attach(
                    SvgField(
                        bit_width=field._pt_width,
                        name="" if name == "_padding" else name,
                        msb=msb,
                        style=ElementStyle.HATCHED
                        if name == "_padding"
                        else ElementStyle.NORMAL,
                    )
                )
            msb -= field._pt_width

    _recurse(resolved())

    # Run the rendering operation
    if output:
        output.write_text(svg.render(), encoding="utf-8")
    else:
        print(svg.render())


@main.command()
@click.argument(
    "mode", type=click.Choice(("package", "register"), case_sensitive=False)
)
@click.argument("language", type=click.Choice(("sv",), case_sensitive=False))
@click.argument("outdir", type=click.Path(file_okay=False, path_type=Path))
@click.argument("selection", type=str, nargs=-1)
@click.pass_context
def code(ctx, mode: str, language: str, outdir: Path, selection: list[str]):
    """Render Packtype package definitions using a language template"""
    # Resolve selection to a struct or union
    resolved = ctx.obj.get("baseline", [])
    if selection:
        all_resolved = []
        for str_path in selection:
            all_resolved.append(
                resolve_to_object(
                    resolved,
                    *str_path.split("."),
                    acceptable=(Package, File),
                )
            )
        resolved = all_resolved
    # Filter out non-matching types
    tmpl_list = None
    match mode.lower():
        case "package":
            resolved = [x for x in resolved if x._PT_BASE is Package]
            tmpl_list = {"sv": (("package.sv.mako", ".sv"),)}
        case "register":
            resolved = [x for x in resolved if x._PT_BASE is File]
            tmpl_list = {
                "sv": (
                    ("register_file.sv.mako", "_rf.sv"),
                    ("register_pkg.sv.mako", "_pkg.sv"),
                )
            }
        case _:
            raise Exception(f"{mode} mode is not supported")
    # Create output directory if it doesn't already exist
    outdir.mkdir(parents=True, exist_ok=True)
    log.debug(f"Using output directory: {outdir.absolute()}")
    # Render
    tmpl_dir = Path(__file__).absolute().parent / "templates"
    lookup = TemplateLookup(
        directories=[tmpl_dir],
        imports=[
            "from datetime import datetime",
            "import math",
            "import re",
            "import packtype.templates.common as tc",
        ],
    )
    context = {}
    for cls in (
        Alias,
        PackedArray,
        Enum,
        Packing,
        Scalar,
        Struct,
        Union,
        NumericPrimitive,
        Register,
        Behaviour,
    ):
        context[cls.__name__] = cls
    # Iterate baselines to render
    for baseline_cls in resolved:
        base_name = baseline_cls.__name__
        baseline = baseline_cls()
        # Iterate outputs to render
        for tmpl_name, suffix in tmpl_list[language]:
            out_path = outdir / f"{snake_case(base_name)}{suffix}"
            log.debug(f"Rendering {base_name} as {language} to {out_path}")
            with out_path.open("w", encoding="utf-8") as fh:
                try:
                    fh.write(
                        lookup.get_template(tmpl_name).render(
                            baseline=baseline, **context
                        )
                    )
                except:
                    log.error(exceptions.text_error_template().render())
                    raise


# Catch invocation
if __name__ == "__main__":  # pragma: no cover
    try:
        main(prog_name="packtype")
    except AssertionError as e:
        log.error(str(e))
        log.error(traceback.format_exc())
