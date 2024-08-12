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

import click
from mako import exceptions
from mako.lookup import TemplateLookup
from rich.logging import RichHandler
from rich.traceback import install

from .alias import Alias
from .array import Array
from .assembly import Packing
from .enum import Enum
from .package import Package
from .scalar import Scalar
from .struct import Struct
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

# Handle CLI
@click.group()
@click.option("--debug", flag_value=True, default=False, help="Enable debug messages")
@click.option("--only", type=str, multiple=True, help="Packages to render")
@click.argument("spec", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.pass_context
def main(ctx, debug: bool, only: list[str], spec: str):
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
    pkgs = list(Registry.query(Package))
    log.debug(f"Discovered {len(pkgs)} package definitions")
    # Filter out just those that were selected
    if only:
        only = {str(x).lower() for x in only}
        pkgs = [x for x in pkgs if x.__name__.lower() in only]
    # Attach packages to context
    ctx.obj["pkgs"] = pkgs


@main.command()
@click.argument("selection", type=str)
@click.argument("output", type=click.Path(dir_okay=False, path_type=Path), default=None, required=False)
@click.pass_context
def svg(ctx, selection: str, output: Path):
    # Resolve selection to a struct or union
    resolved = None
    for segment in selection.split("."):
        if resolved is None:
            matched = [x for x in ctx.obj.get("pkgs", []) if x.__name__ == segment]
            if len(matched) != 1:
                raise Exception(f"Cannot resolve package '{segment}'")
            resolved = matched[0]
        else:
            if (nxt_rslv := getattr(resolved, segment, None)) is None:
                raise Exception(f"Cannot resolve '{segment}' within '{resolved.__name__}'")
            resolved = nxt_rslv
    # Check the type is acceptable
    if not hasattr(resolved, "_PT_BASE"):
        raise Exception(
            f"Selection {selection} resolved to a non-Packtype object"
        )
    elif not issubclass(resolved, (Struct, Union)):
        raise Exception(
            f"Selection {selection} resolved to an object of type "
            f"{resolved._PT_BASE.__name__} which cannot be rendered as an SVG"
        )

@main.command()
@click.argument("language", type=click.Choice(("sv",), case_sensitive=False))
@click.argument("outdir", type=click.Path(file_okay=False, path_type=Path), default=Path.cwd())
@click.pass_context
def code(ctx, language: str, outdir: Path):
    """Render Packtype package definitions using a language template"""
    # Template map
    tmpl_list = {
        "sv": ("package.sv.mako", ".sv"),
    }
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
    context = {
        "Alias": Alias,
        "Array": Array,
        "Enum": Enum,
        "Packing": Packing,
        "Scalar": Scalar,
        "Struct": Struct,
        "Union": Union,
    }
    # Iterate packages to render
    for pkg_cls in ctx.obj.get("pkgs", []):
        pkg_name = pkg_cls.__name__
        pkg = pkg_cls()
        # Iterate outputs to render
        tmpl_name, suffix = tmpl_list[language]
        out_path = outdir / f"{snake_case(pkg_name)}{suffix}"
        log.debug(f"Rendering {pkg_name} as {language} to {out_path}")
        with out_path.open("w", encoding="utf-8") as fh:
            try:
                fh.write(lookup.get_template(tmpl_name).render(pkg=pkg, **context))
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
