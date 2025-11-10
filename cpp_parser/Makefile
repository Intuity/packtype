# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

.DEFAULT_GOAL := all

PATH := /opt/homebrew/opt/bison/bin:$(PATH)
export PATH

OUT_DIR := out
CXX     := g++ -g

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

$(OUT_DIR)/y.tab.c $(OUT_DIR)/y.tab.h $(OUT_DIR)/y.output: packtype.y | $(OUT_DIR)
	@echo "# Running Bison on $<"
	/opt/homebrew/opt/bison/bin/bison --file-prefix=$(OUT_DIR)/y -vdt $(abspath $<)

$(OUT_DIR)/y.tab.o: $(OUT_DIR)/y.tab.c $(OUT_DIR)/y.tab.h | $(OUT_DIR)
	@echo "# Running G++ on $<"
	$(CXX) -I$(OUT_DIR) -c $< -o $@

$(OUT_DIR)/tokens.c: packtype.l $(OUT_DIR)/y.tab.h | $(OUT_DIR)
	@echo "# Running flex on $<"
	flex -t $< > $@

$(OUT_DIR)/tokens.o: $(OUT_DIR)/tokens.c | $(OUT_DIR)
	@echo "# Running G++ on $<"
	$(CXX) -I$(OUT_DIR) -c $< -o $@

$(OUT_DIR)/main.o: main.cpp | $(OUT_DIR)
	@echo "# Running G++ on $<"
	$(CXX) -I$(OUT_DIR) -c $< -o $@

$(OUT_DIR)/parser: $(OUT_DIR)/main.o $(OUT_DIR)/tokens.o $(OUT_DIR)/y.tab.o | $(OUT_DIR)
	@echo "# Linking parser"
	$(CXX) $^ -o $@

all: $(OUT_DIR)/parser

test: $(OUT_DIR)/parser
	@echo "# Running tests"
	./$(OUT_DIR)/parser ./tests/simple.pt

clean:
	rm -rf $(OUT_DIR)
