# Copyright 2021, Peter Birch, mailto:peter@lightlogic.co.uk
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
import inspect
import logging
from pathlib import Path

import click
from mako.lookup import TemplateLookup
from rich.logging import RichHandler
from rich.traceback import install

from .base import Base
from .constant import Constant
from .enum import Enum
from .instance import Instance
from .package import Package
from .scalar import Scalar
from .struct import Struct
from .templates.common import snake_case
from .union import Union

# Setup logging
logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("packtype")
log.setLevel(logging.INFO)

# Setup exception handling
install()

# Language aliases
aliases = {
    "python"       : "py",
    "c++"          : "cpp",
    "systemverilog": "sv",
}

# Handle CLI
@click.command()
@click.option("--render", "-r", type=str, multiple=True,        help="Language to render")
@click.option("--debug",        flag_value=True, default=False, help="Enable debug messages")
@click.argument("spec",   type=click.Path(exists=True, dir_okay=False))
@click.argument("outdir", type=click.Path(file_okay=False), default=".")
def main(render, debug, spec, outdir):
    """ Renders packtype definitions from a SPEC into output files """
    # Set log verbosity
    if debug: log.setLevel(logging.DEBUG)
    # Convert spec and outdir to pathlib objects
    spec   = Path(spec)
    outdir = Path(outdir)
    log.debug(f"Using specification   : {spec.absolute()}")
    log.debug(f"Using output directory: {outdir.absolute()}")
    # Import library
    imp_spec = importlib.util.spec_from_file_location(spec.stem, spec.absolute())
    pt_spec  = importlib.util.module_from_spec(imp_spec)
    imp_spec.loader.exec_module(pt_spec)
    # Look for packtype Base objects
    pt_objs = inspect.getmembers(pt_spec, predicate=lambda x: isinstance(x, Base))
    log.debug(f"Discovered {len(pt_objs)} packtype objects")
    # Filter for packages
    pt_pkgs = list(filter(lambda x: isinstance(x[1], Package), pt_objs))
    log.debug(f"Discovered {len(pt_pkgs)} packtype packages")
    # Create output directory if it doesn't already exist
    if not outdir.exists(): outdir.mkdir(parents=True)
    # Render
    tmpl_dir = Path(__file__).absolute().parent / "templates"
    mk_lkp   = TemplateLookup(
        directories=[tmpl_dir],
        imports    =[
            "from datetime import datetime",
            "import math",
            "import re",
            "import packtype.templates.common as tc",
        ],
    )
    ctx      = {
        "Constant": Constant, "Enum": Enum, "Instance": Instance,
        "Package": Package, "Scalar": Scalar, "Struct": Struct, "Union": Union,
    }
    for lang in render:
        # Resolve the language and any aliases
        lang  = aliases.get(lang.lower(), lang.lower())
        # Locate the associated template
        found = list(tmpl_dir.glob(f"lang_{lang}.*.mako"))
        assert len(found) == 1, f"Failed to locate template for {lang}"
        tmpl  = mk_lkp.get_template(found[0].name)
        # Determine the suffix
        suffix = "".join(found[0].suffixes[:-1])
        # Render every package against the template
        for _, pkg in pt_pkgs:
            with open(outdir / f"{snake_case(pkg._pt_name)}{suffix}", "w") as fh:
                fh.write(tmpl.render(
                    name   =pkg._pt_name,
                    package=pkg,
                    source =spec.absolute(),
                    **ctx
                ))

# Catch invocation
if __name__ == "__main__":
    try:
        main(prog_name="packtype")
    except AssertionError as e:
        log.error(str(e))
