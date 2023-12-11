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

# Template map
tmpl_list = {
    "systemverilog": ("package.sv.mako", ".sv"),
    "sv": ("package.sv.mako", ".sv"),
}


# Handle CLI
@click.command()
@click.option("--render", "-r", type=str, multiple=True, help="Language to render")
@click.option("--debug", flag_value=True, default=False, help="Enable debug messages")
@click.option("--only", type=str, multiple=True, help="Packages to render")
@click.argument("spec", type=click.Path(exists=True, dir_okay=False))
@click.argument("outdir", type=click.Path(file_okay=False), default=".")
def main(render: list[str], debug: bool, only: list[str], spec: str, outdir: str):
    """Renders packtype definitions into different forms"""
    # Set log verbosity
    if debug:
        log.setLevel(logging.DEBUG)
    # Check render requests
    render = {x.lower() for x in render}
    unknown = render.difference(tmpl_list.keys())
    assert not unknown, f"No template registered to render {', '.join(render)}"
    # Convert spec and outdir to pathlib objects
    spec = Path(spec)
    outdir = Path(outdir)
    log.debug(f"Using specification   : {spec.absolute()}")
    log.debug(f"Using output directory: {outdir.absolute()}")
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
    # Create output directory if it doesn't already exist
    outdir.mkdir(parents=True, exist_ok=True)
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
    for pkg_cls in pkgs:
        pkg_name = pkg_cls.__name__
        pkg = pkg_cls()
        # Iterate outputs to render
        for lang in render:
            tmpl_name, suffix = tmpl_list[lang]
            out_path = outdir / f"{snake_case(pkg_name)}{suffix}"
            log.debug(f"Rendering {pkg_name} as {lang} to {out_path}")
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
