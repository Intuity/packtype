# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import traceback

from packtype.start import get_log, main, setup_logging_and_exceptions

# Catch invocation
if __name__ == "__main__":  # pragma: no cover
    try:
        setup_logging_and_exceptions()
        main(prog_name="packtype")
    except AssertionError as e:
        get_log().error(str(e))
        get_log().error(traceback.format_exc())
