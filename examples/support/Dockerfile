# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

FROM ubuntu:24.04

# Base packages
RUN apt update -y
RUN apt-get install -y \
        build-essential \
        ca-certificates \
        curl \
        git \
        libbz2-dev \
        libffi-dev \
        liblzma-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        make \
        pkg-config \
        tk-dev \
        wget \
        xz-utils \
        zlib1g-dev

# pyenv
RUN curl https://pyenv.run | bash
RUN echo '# .bashrc' >> /root/.bashrc && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /root/.bashrc && \
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> /root/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> /root/.bashrc

# Install Python 3.12
RUN export PYENV_ROOT="/root/.pyenv" && \
    export PATH="$PYENV_ROOT/bin:$PATH" && \
    eval "$(pyenv init -)" && \
    pyenv install 3.12 && \
    pyenv global 3.12

# Install poetry
RUN export PYENV_ROOT="/root/.pyenv" && \
    export PATH="$PYENV_ROOT/bin:$PATH" && \
    eval "$(pyenv init -)" && \
    python3 -m pip install poetry

# Install Verilator
RUN cd /tmp && \
    git clone https://github.com/verilator/verilator && \
    cd verilator && \
    git checkout v5.024
RUN apt install -y autoconf python3 flex bison help2man
RUN cd /tmp/verilator && \
    autoconf
RUN cd /tmp/verilator && \
    ./configure
RUN cd /tmp/verilator && \
    make -j12
RUN cd /tmp/verilator && \
    make install

#
RUN apt install -y perl-doc
