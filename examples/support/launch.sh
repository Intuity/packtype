#!/bin/bash

# Activate pyenv
export PYENV_ROOT="/root/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Install poetry environment
poetry lock
poetry install --no-root --quiet --with=dev
export VIRTUAL_ENV_DISABLE_PROMPT=1
source $(poetry env info --path)/bin/activate
