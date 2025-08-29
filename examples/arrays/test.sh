#!/bin/bash

# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

# Credit to Dave Dopson: https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Setup PYTHONPATH to get access to packtype
export PYTHONPATH=${this_dir}/../..:$PYTHONPATH

# Invoke packtype on Python syntax
python3 -m packtype --debug code package sv ${this_dir}/out_py ${this_dir}/spec.py

# Invoke packtype on Packtype syntax
python3 -m packtype --debug code package sv ${this_dir}/out_pt ${this_dir}/spec.pt

