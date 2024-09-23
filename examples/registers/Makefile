# Copyright 2023, Peter Birch, mailto:peter@intuity.io
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

# ==============================================================================
# Packtype
# ==============================================================================

# Extend PYTHONPATH
export PYTHONPATH := $(PYTHONPATH):$(abspath ../..)

# Python input files
PY_SRCS += datastructures.py
PY_SRCS += registers.py

# Render output
OUT_DIR ?= out

# Include directories
INC_DIRS += ../../packtype/common

# RTL source files
SV_SRCS += ../../packtype/common/pt_fifo.sv

# RTL target files
SV_TGTS += $(OUT_DIR)/data_structures.sv
SV_TGTS += $(OUT_DIR)/control_pkg.sv
SV_TGTS += $(OUT_DIR)/control_rf.sv

# ==============================================================================
# cocotb
# ==============================================================================

SIM             ?= verilator
TOPLEVEL_LANG   ?= verilog
TOPLEVEL        ?= control_rf
MODULE          ?= testbench
VERILOG_SOURCES ?= $(SV_SRCS) $(SV_TGTS)
EXTRA_ARGS      += --trace --trace-structs --trace-fst

include $(shell cocotb-config --makefiles)/Makefile.sim

# ==============================================================================
# Rules
# ==============================================================================

$(SV_TGTS): $(PY_SRCS)
	python3 -m packtype datastructures.py code package sv $(OUT_DIR)
	python3 -m packtype --debug registers.py code register sv $(OUT_DIR)

.PHONY: lint
lint: $(SV_SRCS) $(SV_TGTS)
	verilator --lint-only \
	          -Wall \
	          --top-module control_rf \
	          $(addprefix +incdir+,$(INC_DIRS)) \
	          verilator.vlt \
	          $(SV_SRCS) \
	          $(SV_TGTS)

.PHONY: sim
sim: results.xml

.PHONY: clean
clean::
	rm -f $(SV_TGTS)
