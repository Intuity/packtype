#!/bin/bash

# Work out the directory where this script is
EXAMPLE_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)

# Work out the repository root
REPO_ROOT=$(readlink -f $EXAMPLE_DIR/..)

# Build Docker container
docker build -t packtype $EXAMPLE_DIR/support

# Run Docker
docker run --rm \
           -it \
           --mount type=bind,source=$EXAMPLE_DIR/support/launch.sh,target=/launch.sh,readonly \
           --mount type=bind,source=$REPO_ROOT,target=/work \
           --workdir /work \
           packtype \
           /bin/bash --init-file /launch.sh
