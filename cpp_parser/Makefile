.DEFAULT_GOAL := all

OUT_DIR := out
CXX     := g++ -g

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

$(OUT_DIR)/y.tab.c $(OUT_DIR)/y.tab.h $(OUT_DIR)/y.output: packtype.y | $(OUT_DIR)
	@echo "# Running Bison on $<"
	bison --file-prefix=$(OUT_DIR)/y -vdty $(abspath $<)

$(OUT_DIR)/y.tab.o: $(OUT_DIR)/y.tab.c $(OUT_DIR)/y.tab.h | $(OUT_DIR)
	@echo "# Running G++ on $<"
	$(CXX) -I$(OUT_DIR) -c $< -o $@

$(OUT_DIR)/tokens.c: packtype.l $(OUT_DIR)/y.tab.h | $(OUT_DIR)
	@echo "# Running flex on $<"
	flex -t $< > $@

$(OUT_DIR)/tokens.o: $(OUT_DIR)/tokens.c | $(OUT_DIR)
	@echo "# Running G++ on $<"
	$(CXX) -I$(OUT_DIR) -c $< -o $@

all: $(OUT_DIR)/tokens.o $(OUT_DIR)/y.tab.o

clean:
	rm -rf $(OUT_DIR)
