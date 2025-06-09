#!/bin/bash

# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

# Credit to Dave Dopson: https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $this_dir

# Setup PYTHONPATH to get access to packtype
export PYTHONPATH=${this_dir}/../..:$PYTHONPATH

# Invoke packtype to generate package
python3 -m packtype datastructures.py code package sv ${this_dir}/out

# Invoke packtype to generate registers
python3 -m packtype --debug registers.py code register sv ${this_dir}/out

