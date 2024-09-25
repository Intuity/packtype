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

module pt_axi4lite_bridge #(
      parameter  AXI_ADDR_W     = 32
    , parameter  RF_ADDR_W      = 32
    , parameter  DATA_W         = 64
    , parameter  RSP_BUFF_DEPTH =  8
    , localparam STRB_W         = DATA_W / 8
    , localparam PROT_W         =  3
    , localparam RESP_W         =  2
) (
      input  logic                  i_clk
    , input  logic                  i_rst
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

// =============================================================================
// Signals
// =============================================================================

logic [AXI_ADDR_W-1:0] next_awaddr, awaddr_d, awaddr_q,
                       next_araddr, araddr_d, araddr_q;
logic [DATA_W-1:0]     next_wdata, wdata_d, wdata_q;
logic                  next_awvalid, awvalid_d, awvalid_q,
                       next_arvalid, arvalid_d, arvalid_q,
                       next_wvalid,  wvalid_d,  wvalid_q;

logic accept_write, accept_read;
logic pending_read_q, pending_write_q;

response_t rb_wr_data, rb_rd_data;
logic      rb_wr_valid, rb_rd_valid, rb_rd_ready, rb_hwm;

// =============================================================================
// AXI4-Lite Request to Register Interface
// =============================================================================

// Write address capturing
assign next_awaddr  = awvalid_q ? awaddr_q : i_awaddr;
assign next_awvalid = i_awvalid || awvalid_q;
assign o_awready    = !awvalid_q;

assign awaddr_d     = next_awaddr;
assign awvalid_d    = i_awvalid && !o_awready;

// Write data capturing
assign next_wdata   = wvalid_q  ? wdata_q  : i_wdata;
assign next_wvalid  = i_wvalid || wvalid_q;
assign o_wready     = !wvalid_q;

assign wdata_d      = next_wdata;
assign wvalid_d     = i_wvalid && !o_wready;

// Read address capturing
assign next_araddr  = arvalid_q ? araddr_q : i_araddr;
assign next_arvalid = i_arvalid || arvalid_q;
assign o_arready    = !arvalid_q;

assign araddr_d     = next_araddr;
assign arvalid_d    = i_arvalid && !o_arready;

// Decide what we're accepting
assign accept_write = (!pending_write_q || !next_arvalid) &&
                      next_awvalid &&
                      next_wvalid &&
                      !rb_hwm;
assign accept_read  = !accept_write &&
                      next_arvalid &&
                      !rb_hwm;

// Form request
assign o_rf_address = accept_write ? next_awaddr[RF_ADDR_W-1:0]
                                   : next_araddr[RF_ADDR_W-1:0];
assign o_rf_wr_data = next_wdata;
assign o_rf_write   = accept_write;
assign o_rf_enable  = accept_write || accept_read;

// Register any unhandled requests
always_ff @(posedge i_clk, posedge i_rst) begin : ff_access
    if (i_rst) begin
        awaddr_q  <= AXI_ADDR_W'(0);
        araddr_q  <= AXI_ADDR_W'(0);
        wdata_q   <= DATA_W'(0);
        awvalid_q <= 1'b0;
        arvalid_q <= 1'b0;
        wvalid_q  <= 1'b0;
    end else begin
        awaddr_q  <= awaddr_d;
        araddr_q  <= araddr_d;
        wdata_q   <= wdata_d;
        awvalid_q <= awvalid_d;
        arvalid_q <= arvalid_d;
        wvalid_q  <= wvalid_d;
    end
end

// =============================================================================
// Response Capture and Buffering
// =============================================================================

// Track pending request
always_ff @(posedge i_clk, posedge i_rst)
    if (i_rst)
        { pending_read_q, pending_write_q } <= 2'd0;
    else
        { pending_read_q, pending_write_q } <= { accept_read, accept_write };

// Fill in response
assign rb_wr_data = '{
      write: pending_write_q
    , data : i_rf_rd_data
    , error: i_rf_error
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
    , .o_empty    (                )
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
// Unused
// =============================================================================

// TODO @intuity: Raise a SLVERR if not all strobe bits set

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
