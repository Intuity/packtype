#!/bin/bash

# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

# Credit to Dave Dopson: https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Create a virtual environment
python3 -m virtualenv ${this_dir}/venv
source ${this_dir}/venv/bin/activate
python3 -m pip install ${this_dir}/..

# Run all tests in subdirectories
passed=0
failed=0
for test_sh in ${this_dir}/*/test.sh; do
    test_dir=$(dirname $test_sh)
    test_name=$(basename $test_dir)
    cd $test_dir
    echo "# Running test $test_name"
    ./test.sh
    if [[ "$?" != "0" ]]; then
        failed=$((failed + 1))
    else
        passed=$((passed + 1))
    fi
    cd ${this_dir}
done

# Clean-up
rm -rf ${this_dir}/venv

# Report
echo "# Tests Passed: $passed, Tests Failed: $failed"

if (( $failed > 0 )); then
    echo "[ERROR] Not all tests passed"
    exit 1
fi
