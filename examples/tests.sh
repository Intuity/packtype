#!/bin/bash

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

# Credit to Dave Dopson: https://stackoverflow.com/questions/59895/how-can-i-get-the-source-directory-of-a-bash-script-from-within-the-script-itsel
this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Create a virtual environment
python3 -m virtualenv ${this_dir}/venv
source ${this_dir}/venv/bin/activate
python3 ${this_dir}/../setup.py develop

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
