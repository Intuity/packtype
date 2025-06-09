# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

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
SV_EARLY_SRCS += ../../packtype/common/pt_fifo.sv
SV_LATE_SRCS  +=

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
VERILOG_SOURCES ?= $(SV_SRCS) $(SV_TGTS) $(SV_LATE_SRCS)
EXTRA_ARGS      += --trace --trace-structs --trace-fst

include $(shell cocotb-config --makefiles)/Makefile.sim

# ==============================================================================
# Rules
# ==============================================================================

$(SV_TGTS): $(PY_SRCS)
	python3 -m packtype datastructures.py code package sv $(OUT_DIR)
	python3 -m packtype --debug registers.py code register sv $(OUT_DIR)

.PHONY: lint
lint: $(VERILOG_SOURCES)
	verilator --lint-only \
	          -Wall \
	          --top-module $(TOPLEVEL) \
	          $(addprefix +incdir+,$(INC_DIRS)) \
	          verilator.vlt \
	          $(VERILOG_SOURCES)

.PHONY: sim
sim: results.xml

.PHONY: clean
clean::
	rm -f $(SV_TGTS)
