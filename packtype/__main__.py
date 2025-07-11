# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import traceback

from packtype.common.logging import get_log, setup_logging_and_exceptions
from packtype.start import main

# Catch invocation
if __name__ == "__main__":  # pragma: no cover
    try:
        setup_logging_and_exceptions()
        main(prog_name="packtype")
    except AssertionError as e:
        get_log().error(str(e))
        get_log().error(traceback.format_exc())
