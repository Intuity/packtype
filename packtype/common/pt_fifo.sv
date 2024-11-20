// Copyright 2023, Peter Birch, mailto:peter@intuity.io
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module pt_fifo #(
      parameter type DATA_T  = logic [31:0]
    , parameter      DEPTH   = 8
    , parameter      HWM     = DEPTH - 1
    , localparam     COUNT_W = $clog2(DEPTH+1)
) (
      input  logic               i_clk
    , input  logic               i_rst
    // Push stream
    , input  DATA_T              i_wr_data
    , input  logic               i_wr_valid
    , output logic               o_wr_ready
    // Pop stream
    , output DATA_T              o_rd_data
    , output logic               o_rd_valid
    , input  logic               i_rd_ready
    // Status
    , output logic [COUNT_W-1:0] o_level
    , output logic               o_full
    , output logic               o_hwm
    , output logic               o_empty
);

typedef logic [COUNT_W-1:0] count_t;

DATA_T [DEPTH-1:0] entries_d, entries_q;
count_t            head_q, tail_q, level_q;
logic              push, pop;

always_ff @(posedge i_clk, posedge i_rst) begin : ff_entries
    if (i_rst) begin
        entries_q <= (DEPTH*$bits(DATA_T))'(0);
    end else begin
        entries_q <= entries_d;
    end
end

// =============================================================================
// Status
// =============================================================================

assign o_level = level_q;
assign o_full  = (level_q == COUNT_W'(DEPTH));
assign o_hwm   = (level_q >= COUNT_W'(HWM));
assign o_empty = (level_q == COUNT_W'(0));

// =============================================================================
// Identify Push & Pop
// =============================================================================

assign push = i_wr_valid && o_wr_ready;
assign pop  = o_rd_valid && i_rd_ready;

// =============================================================================
// Track Pointers and Level
// =============================================================================

always_ff @(posedge i_clk, posedge i_rst) begin : ff_head
    if (i_rst)
        head_q <= COUNT_W'(0);
    else if (push)
        head_q <= (head_q == COUNT_W'(DEPTH - 'd1)) ? COUNT_W'(0)
                                                    : { head_q + COUNT_W'(1) };
end

always_ff @(posedge i_clk, posedge i_rst) begin : ff_tail
    if (i_rst)
        tail_q <= COUNT_W'(0);
    else if (pop)
        tail_q <= (tail_q == COUNT_W'(DEPTH - 'd1)) ? COUNT_W'(0)
                                                    : { tail_q + COUNT_W'(1) };
end

always_ff @(posedge i_clk, posedge i_rst) begin : ff_level
    if (i_rst)
        level_q <= COUNT_W'(0);
    else
        level_q <= { level_q - COUNT_W'(pop) + COUNT_W'(push) };
end

// =============================================================================
// Push
// =============================================================================

generate
for (genvar idx = 0; idx < DEPTH; idx++) begin : gen_push
    assign entries_d[idx] = (push && head_q == COUNT_W'(idx)) ? i_wr_data
                                                              : entries_q[idx];
end
endgenerate

assign o_wr_ready = !o_full;

// =============================================================================
// Pop
// =============================================================================

assign o_rd_data  = entries_q[tail_q];
assign o_rd_valid = !o_empty;

endmodule : pt_fifo
