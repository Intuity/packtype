#!/bin/bash

# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

# Credit to Dave Dopson: https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Setup PYTHONPATH to get access to packtype
export PYTHONPATH=${this_dir}/../..:$PYTHONPATH

# Invoke packtype
python3 -m packtype --debug spec.py code package sv ${this_dir}/out

# Render SVG
python3 -m packtype --debug spec.py svg MyPackage.PingPongMessage ./out/out.svg
