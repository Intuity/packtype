# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import logging

from rich.logging import RichHandler
from rich.traceback import install


def get_log() -> logging.Logger:
    """Get the logger for the packtype module."""
    return logging.getLogger("packtype")


def setup_logging_and_exceptions():
    # Setup logging
    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    get_log().setLevel(logging.INFO)

    # Setup exception handling
    install()
