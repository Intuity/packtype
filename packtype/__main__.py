# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
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

import ast
import importlib.util
import logging
import traceback
from pathlib import Path
from types import SimpleNamespace

import click
from rich.logging import RichHandler
from rich.traceback import install

from .alias import Alias
from .array import PackedArray
from .assembly import Packing
from .base import Base
from .constant import Constant
from .enum import Enum
from .package import Package
from .primitive import NumericPrimitive
from .registers import Behaviour, File, Register
from .scalar import Scalar
from .struct import Struct
from .union import Union
from .wrap import Registry
from . import utils

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
                raise click.ClickException(f"Cannot resolve baseline '{segment}'")
            resolved = matched[0]
        else:
            if (nxt_rslv := getattr(resolved, segment, None)) is None:
                raise click.ClickException(
                    f"Cannot resolve '{segment}' within '{resolved.__name__}'"
                )
            resolved = nxt_rslv
    # Check the type is acceptable
    if not hasattr(resolved, "_PT_BASE"):
        raise click.ClickException(f"Selection {path} resolved to a non-Packtype object")
    elif acceptable is not None and not issubclass(resolved, acceptable):
        raise click.ClickException(
            f"Selection {'.'.join(path)} resolved to an object of type "
            f"{resolved._PT_BASE.__name__} which is incompatible with this command"
        )
    return resolved


# Handle CLI
@click.group()
@click.option("--debug", flag_value=True, default=False, help="Enable debug messages")
@click.argument("spec", type=str)
@click.pass_context
def main(ctx, debug: bool, spec: str):
    """Renders packtype definitions into different forms"""
    ctx.ensure_object(dict)
    # Set log verbosity
    if debug:
        log.setLevel(logging.DEBUG)
    # Does the spec look like a path?
    if Path(spec).exists() and Path(spec).is_file():
        spec = Path(spec)
        log.debug(f"Importing specification as a file: {spec.absolute()}")
        imp_spec = importlib.util.spec_from_file_location(spec.stem, spec.absolute())
        imp_spec.loader.exec_module(importlib.util.module_from_spec(imp_spec))
    # Otherwise, assume it is a module import
    else:
        log.debug(f"Importing specification as a module: {spec}")
        importlib.import_module(spec)
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
        acceptable=(Struct,),
    )

    # Run the rendering operation
    if output:
        output.write_text(resolved()._pt_as_svg(), encoding="utf-8")
    else:
        print(resolved()._pt_as_svg())


@main.command()
@click.option(
    "-o", "--option", type=str, multiple=True, help="Options in the form <KEY>=<VALUE>",
)
@click.argument(
    "mode", type=click.Choice(("package", "register"), case_sensitive=False)
)
@click.argument("language", type=click.Choice(("sv","py","cpp"), case_sensitive=False))
@click.argument("outdir", type=click.Path(file_okay=False, path_type=Path))
@click.argument("selection", type=str, nargs=-1)
@click.pass_context
def code(ctx, option: list[str], mode: str, language: str, outdir: Path, selection: list[str]):
    """Render Packtype package definitions using a language template"""

    # Deferred imports for optional libraries
    from mako import exceptions
    from mako.lookup import TemplateLookup
    from .templates.common import snake_case

    # Digest options
    options = {}
    for opt_str in option:
        if opt_str.count("=") != 1:
            raise Exception(f"Incorrect number of = in '{opt_str}'")
        key, value = opt_str.split("=")
        options[key.strip().lower()] = ast.literal_eval(value.strip())
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
    # Detect missing selection
    if not resolved:
        raise Exception("Failed to resolve any objects to render")
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
                ),
                "py": (
                    ("register_access.py.mako", "_access.py"),
                ),
                "cpp": (
                    ("register_access.hpp.mako", "_access.hpp"),
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
    context = {"options": options, "utils": utils}
    for cls in (
        Alias,
        Constant,
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
