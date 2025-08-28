# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import ast
import functools
import importlib.util
import logging
from pathlib import Path
from types import SimpleNamespace

import click

from . import utils
from .common.logging import get_log
from .grammar import parse
from .registers import Behaviour, File, Register
from .templates.common import camel_case, snake_case
from .types.alias import Alias
from .types.array import PackedArray
from .types.assembly import Packing
from .types.base import Base
from .types.constant import Constant
from .types.enum import Enum
from .types.package import Package
from .types.primitive import NumericPrimitive
from .types.scalar import Scalar, ScalarType
from .types.struct import Struct
from .types.union import Union
from .types.wrap import Registry


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
            f"Selection {path} resolved to an object of type "
            f"{resolved._PT_BASE.__name__} which cannot be rendered as an SVG"
        )
    return resolved


def load_specification(spec_files: list[str], keep_expression: bool) -> list[Base]:
    log = get_log()

    # If multiple specifications are provided, check they all use .pt format
    if len(spec_files) > 1:
        if any(not x.lower().endswith((".pt", ".packtype", ".ptype")) for x in spec_files):
            raise click.ClickException(
                "Multiple specifications provided, but not all are Packtype grammar"
            )

    # For each specification, parse and track
    namespaces = {}
    for item in spec_files:
        get_log().debug(f"Loading specification: {item}")
        # Packtype grammar files
        if item.lower().endswith((".pt", ".packtype", ".ptype")):
            package = parse(Path(item), namespaces, keep_expression=keep_expression)
            namespaces[package.__name__] = package
        # If it ends with `.py` assume it's Python
        elif item.endswith(".py"):
            item = Path(item)
            log.debug(f"Importing specification as a file: {item.absolute()}")
            imp_spec = importlib.util.spec_from_file_location(item.stem, item.absolute())
            imp_spec.loader.exec_module(importlib.util.module_from_spec(imp_spec))
        # Otherwise, assume it is a module import
        else:
            log.debug(f"Importing specification as a module: {item}")
            importlib.import_module(item)

    # Query the registry for packages
    baseline = list(Registry.query(Package)) + list(Registry.query(File))
    log.debug(f"Discovered {len(baseline)} baseline definitions")

    return baseline


# Handle CLI
@click.group()
@click.option("--debug", flag_value=True, default=False, help="Enable debug messages")
def main(debug: bool):
    """Renders packtype definitions into different forms"""
    log = get_log()
    # Set log verbosity
    if debug:
        log.setLevel(logging.DEBUG)


@main.command()
@click.argument("spec_files", type=str, nargs=-1)
@click.option("--keep-expression", is_flag=True, help="Attach parsed expressions to constants")
def inspect(spec_files: list[str], keep_expression: bool):
    log = get_log()
    baseline = load_specification(spec_files, keep_expression)
    log.warning("Use the 'baseline' namespace to inspect Packtype definitions")
    breakpoint()  # noqa: T100
    del baseline


@main.command()
@click.argument("selection", type=str)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    required=False,
    help="Output file to write the SVG to. If not provided, prints to stdout.",
)
@click.argument("spec_files", type=str, nargs=-1)
def svg(selection: str, output: Path | None, spec_files: list[str]):
    # Resolve selection to a struct
    resolved = resolve_to_object(
        load_specification(spec_files, keep_expression=False),
        *selection.split("."),
        acceptable=(Struct,),
    )

    # Run the rendering operation
    if output:
        output.write_text(resolved()._pt_as_svg(), encoding="utf-8")
    else:
        print(resolved()._pt_as_svg())  # noqa: T201


@main.command()
@click.option(
    "-o",
    "--option",
    type=str,
    multiple=True,
    help="Options in the form <KEY>=<VALUE>",
)
@click.option(
    "-s",
    "--select",
    type=str,
    multiple=True,
    help="Select objects to render",
)
@click.option(
    "--package-suffix",
    type=str,
    default="",
    help="Suffix to append to package names",
)
@click.option(
    "--constant-suffix",
    type=str,
    default="",
    help="Suffix to append to constant names",
)
@click.option(
    "--type-suffix",
    type=str,
    default="_t",
    help="Suffix to append to type names",
)
@click.option(
    "--package-filter",
    multiple=True,
    type=click.Choice(("none", "snake", "camel", "upper", "lower", "suffix"), case_sensitive=False),
    default=["snake", "lower", "suffix"],
    help="Select filters to apply to type names",
)
@click.option(
    "--constant-filter",
    multiple=True,
    type=click.Choice(("none", "snake", "camel", "upper", "lower", "suffix"), case_sensitive=False),
    default=["snake", "upper"],
    help="Select filters to apply to type names",
)
@click.option(
    "--type-filter",
    multiple=True,
    type=click.Choice(("none", "snake", "camel", "upper", "lower", "suffix"), case_sensitive=False),
    default=["snake", "lower", "suffix"],
    help="Select filters to apply to type names",
)
@click.option("--keep-expression", is_flag=True, help="Attach parsed expressions to constants")
@click.argument("mode", type=click.Choice(("package", "register"), case_sensitive=False))
@click.argument(
    "language",
    type=click.Choice(("sv", "py", "cpp"), case_sensitive=False),
    required=True,
)
@click.argument("outdir", type=click.Path(file_okay=False, path_type=Path))
@click.argument("spec_files", type=str, nargs=-1)
def code(
    option: list[str],
    select: list[str],
    package_suffix: str,
    constant_suffix: str,
    type_suffix: str,
    package_filter: list[str],
    constant_filter: list[str],
    type_filter: list[str],
    mode: str,
    language: str,
    outdir: Path,
    spec_files: list[str],
    keep_expression: bool,
):
    """Render Packtype package definitions using a language template"""
    log = get_log()

    # Load the baseline
    resolved = load_specification(spec_files, keep_expression)

    # Deferred imports for optional libraries
    from mako import exceptions
    from mako.lookup import TemplateLookup

    # Digest options
    options = {}
    for opt_str in option:
        if opt_str.count("=") != 1:
            raise click.ClickException(f"Incorrect number of = in '{opt_str}'")
        key, value = opt_str.split("=")
        options[key.strip().lower()] = ast.literal_eval(value.strip())

    # Resolve selections
    if select:
        all_resolved = []
        for str_path in select:
            all_resolved.append(
                resolve_to_object(
                    resolved,
                    *str_path.split("."),
                    acceptable=(Package, File),
                )
            )
        resolved = all_resolved

    # Resolve constant and type filters
    all_filters = {
        "snake": snake_case,
        "camel": camel_case,
        "upper": lambda x: x.upper(),
        "lower": lambda x: x.lower(),
    }

    compound_package = functools.reduce(
        lambda f, g: lambda x: f(g(x)),
        [
            {**all_filters, "suffix": lambda x: x + package_suffix}[x]
            for x in package_filter
            if x != "none"
        ][::-1],
        lambda x: x,
    )

    compound_constant = functools.reduce(
        lambda f, g: lambda x: f(g(x)),
        [
            {**all_filters, "suffix": lambda x: x + constant_suffix}[x]
            for x in constant_filter
            if x != "none"
        ][::-1],
        lambda x: x,
    )

    compound_type = functools.reduce(
        lambda f, g: lambda x: f(g(x)),
        [
            {**all_filters, "suffix": lambda x: x + type_suffix}[x]
            for x in type_filter
            if x != "none"
        ][::-1],
        lambda x: x,
    )

    # Detect missing select
    if not resolved:
        raise click.ClickException("Failed to resolve any objects to render")

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
                "py": (("register_access.py.mako", "_access.py"),),
                "cpp": (("register_access.hpp.mako", "_access.hpp"),),
            }
        case _:
            raise click.ClickException(f"{mode} mode is not supported")

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
        "options": options,
        "utils": utils,
        "filters": SimpleNamespace(
            package=compound_package,
            constant=compound_constant,
            type=compound_type,
        ),
    }
    for cls in (
        Alias,
        Constant,
        PackedArray,
        Enum,
        Packing,
        Scalar,
        ScalarType,
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
                    fh.write(lookup.get_template(tmpl_name).render(baseline=baseline, **context))
                except:
                    log.error(exceptions.text_error_template().render())
                    raise
