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

// TODO @intuity: Pretty sure the alignment conditions are wrong for AXI writes
//                and won't work where AW and W arrive in different cycles

module pt_axi4lite_bridge #(
      parameter  AXI_ADDR_W     = 32
    , parameter  RF_ADDR_W      = 32
    , parameter  DATA_W         = 64
    , parameter  RSP_BUFF_DEPTH =  8
    , localparam STRB_W         = DATA_W / 8
    , localparam PROT_W         =  3
    , localparam RESP_W         =  2
    , localparam ALIGN_Q_DEPTH  = 2
) (
      input  logic                  i_clk
    , input  logic                  i_rst
    // =========================================================================
    // Status
    // =========================================================================
    , output logic                  o_idle
    // =========================================================================
    // AX4-Lite Upstream
    // =========================================================================
    , input  logic [AXI_ADDR_W-1:0] i_awaddr
    , input  logic [PROT_W-1:0]     i_awprot
    , input  logic                  i_awvalid
    , output logic                  o_awready
    , input  logic [DATA_W-1:0]     i_wdata
    , input  logic [STRB_W-1:0]     i_wstrb
    , input  logic                  i_wvalid
    , output logic                  o_wready
    , output logic [RESP_W-1:0]     o_bresp
    , output logic                  o_bvalid
    , input  logic                  i_bready
    , input  logic [AXI_ADDR_W-1:0] i_araddr
    , input  logic [PROT_W-1:0]     i_arprot
    , input  logic                  i_arvalid
    , output logic                  o_arready
    , output logic [DATA_W-1:0]     o_rdata
    , output logic [RESP_W-1:0]     o_rresp
    , output logic                  o_rvalid
    , input  logic                  i_rready
    // =========================================================================
    // Register Interface Downstream
    // =========================================================================
    , output logic [RF_ADDR_W-1 :0] o_rf_address
    , output logic [DATA_W-1:0]     o_rf_wr_data
    , output logic                  o_rf_write
    , output logic                  o_rf_enable
    , input  logic [DATA_W-1:0]     i_rf_rd_data
    , input  logic                  i_rf_error
);

// =============================================================================
// Typedefs
// =============================================================================

typedef struct packed {
    logic              write;
    logic [DATA_W-1:0] data;
    logic              error;
} response_t;

typedef enum logic [RESP_W-1:0] {
      RESP_OKAY
    , RESP_EXOKAY
    , RESP_SLVERR
    , RESP_DECERR
} axi_resp_t;

typedef struct packed {
    logic [AXI_ADDR_W-1:0] axaddr;
} ax_req_t;

typedef struct packed {
    logic [DATA_W-1:0] wdata;
    logic [STRB_W-1:0] wstrb;
} w_req_t;

// =============================================================================
// Signals
// =============================================================================

// Alignment
ax_req_t aw_wr_data, aw_rd_data;
w_req_t  w_wr_data, w_rd_data;
logic    aw_rd_valid, aw_rd_ready, awq_idle, wq_idle, w_rd_valid, w_rd_ready;

// Request arbitration
logic accept_write, accept_read;
logic pending_read_q, pending_write_q;
logic write_strobe_error_d, write_strobe_error_q;

// Response buffer
response_t rb_wr_data, rb_rd_data;
logic      rb_wr_valid, rb_rd_valid, rb_rd_ready, rb_hwm, rb_idle;

// =============================================================================
// AXI4-Lite Request Alignment
// =============================================================================

assign aw_wr_data = '{ axaddr: i_awaddr };
assign w_wr_data  = '{ wdata : i_wdata,  wstrb : i_wstrb  };

vc_fifo_sync_flop #(
      .DATA_T     ( ax_req_t      )
    , .DEPTH      ( ALIGN_Q_DEPTH )
) u_aw_align_q (
      .i_clk      ( i_clk         )
    , .i_rst      ( i_rst         )
    // Push interface
    , .i_wr_data  ( aw_wr_data    )
    , .i_wr_valid ( i_awvalid     )
    , .o_wr_ready ( o_awready     )
    // Pop interface
    , .o_rd_data  ( aw_rd_data    )
    , .o_rd_valid ( aw_rd_valid   )
    , .i_rd_ready ( aw_rd_ready   )
    // Status
    , .o_level    (               )
    , .o_empty    ( awq_idle      )
    , .o_hwm      (               )
    , .o_full     (               )
);

vc_fifo_sync_flop #(
      .DATA_T     ( w_req_t       )
    , .DEPTH      ( ALIGN_Q_DEPTH )
) u_w_align_q (
      .i_clk      ( i_clk         )
    , .i_rst      ( i_rst         )
    // Push interface
    , .i_wr_data  ( w_wr_data     )
    , .i_wr_valid ( i_wvalid      )
    , .o_wr_ready ( o_wready      )
    // Pop interface
    , .o_rd_data  ( w_rd_data     )
    , .o_rd_valid ( w_rd_valid    )
    , .i_rd_ready ( w_rd_ready    )
    // Status
    , .o_level    (               )
    , .o_empty    ( wq_idle       )
    , .o_hwm      (               )
    , .o_full     (               )
);

// =============================================================================
// AXI4-Lite Request to Register Interface
// =============================================================================

// Decide what we're accepting (alternates between reads and writes)
assign accept_write = (!pending_write_q || !i_arvalid) &&
                      aw_rd_valid &&
                      w_rd_valid &&
                      !rb_hwm;
assign accept_read  = !accept_write &&
                      i_arvalid &&
                      !rb_hwm;

// Error if not all strobe lines set
assign write_strobe_error_d = (w_rd_data.wstrb != {STRB_W{1'b1}});

// Accept traffic
assign aw_rd_ready = accept_write;
assign w_rd_ready  = accept_write;
assign o_arready   = accept_read && |{ !aw_rd_valid
                                     , !w_rd_valid
                                     , !pending_write_q };

// Form request
// NOTE: Suppress write if a strobe error detected
assign o_rf_address = accept_write ? RF_ADDR_W'(aw_rd_data.axaddr)
                                   : RF_ADDR_W'(i_araddr);
assign o_rf_wr_data = w_rd_data.wdata;
assign o_rf_write   = accept_write;
assign o_rf_enable  = (!write_strobe_error_d && accept_write) || accept_read;

// =============================================================================
// Response Capture and Buffering
// =============================================================================

// Track pending request
always_ff @(posedge i_clk, posedge i_rst)
    if (i_rst)
        { pending_read_q, pending_write_q } <= 2'd0;
    else
        { pending_read_q, pending_write_q } <= { accept_read, accept_write };

// Pipeline strobe error
always_ff @(posedge i_clk, posedge i_rst)
    if (i_rst)
        write_strobe_error_q <= 1'b0;
    else
        write_strobe_error_q <= write_strobe_error_d;

// Fill in response
assign rb_wr_data = '{
      write: pending_write_q
    , data : i_rf_rd_data
    , error: i_rf_error || write_strobe_error_q
};

assign rb_wr_valid = pending_read_q || pending_write_q;

// Response buffer
pt_fifo #(
      .DATA_T     ( response_t     )
    , .DEPTH      ( RSP_BUFF_DEPTH )
) u_rsp_buffer (
      .i_clk      ( i_clk          )
    , .i_rst      ( i_rst          )
    // Push stream
    , .i_wr_data  ( rb_wr_data     )
    , .i_wr_valid ( rb_wr_valid    )
    , .o_wr_ready (                )
    // Pop stream
    , .o_rd_data  ( rb_rd_data     )
    , .o_rd_valid ( rb_rd_valid    )
    , .i_rd_ready ( rb_rd_ready    )
    // Status
    , .o_level    (                )
    , .o_full     (                )
    , .o_hwm      ( rb_hwm         )
    , .o_empty    ( rb_idle        )
);

// =============================================================================
// Buffered Responses -> AXI4-Lite Response
// =============================================================================

// Drive AXI responses
assign o_bresp  = rb_rd_data.error ? RESP_SLVERR : RESP_OKAY;
assign o_bvalid = rb_rd_valid && rb_rd_data.write;

assign o_rdata  = rb_rd_data.data;
assign o_rresp  = rb_rd_data.error ? RESP_SLVERR : RESP_OKAY;
assign o_rvalid = rb_rd_valid && !rb_rd_data.write;

assign rb_rd_ready = (i_bready &&  rb_rd_data.write) ||
                     (i_rready && !rb_rd_data.write);

// =============================================================================
// Status
// =============================================================================

assign o_idle = &{ !i_awvalid
                 , !i_wvalid
                 , !i_arvalid
                 , awq_idle
                 , wq_idle
                 , !pending_write_q
                 , !pending_read_q
                 , rb_idle };

// =============================================================================
// Unused
// =============================================================================

logic _unused;
assign _unused = &{
      1'b0
    , i_awprot
    , i_arprot
    , i_wstrb
    , i_awaddr[AXI_ADDR_W-1:RF_ADDR_W]
    , i_araddr[AXI_ADDR_W-1:RF_ADDR_W]
};

endmodule : pt_axi4lite_bridge
