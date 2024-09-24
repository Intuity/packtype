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
      parameter  ADDR_W = 32
    , parameter  DATA_W = 64
    , localparam STRB_W = DATA_W / 8
) (
      input  logic i_clk
    , input  logic i_rst
    // =========================================================================
    // AX4-Lite Upstream
    // =========================================================================
    , input  logic [ADDR_W-1:0] i_awaddr
    , input  logic              i_awvalid
    , output logic              o_awready
    , input  logic [DATA_W-1:0] i_wdata
    , input  logic [STRB_W-1:0] i_wstrb
    , input  logic              i_wvalid
    , output logic              o_wready
    , output logic [       1:0] o_bresp
    , output logic              o_bvalid
    , input  logic              i_bready
    , input  logic [ADDR_W-1:0] i_araddr
    , input  logic              i_arvalid
    , output logic              o_arready
    , output logic [DATA_W-1:0] o_rdata
    , output logic [       1:0] o_rresp
    , output logic              o_rvalid
    , input  logic              i_rready
    // =========================================================================
    // Register Interface Downstream
    // =========================================================================
    , output logic [ADDR_W-1:0] o_rf_address
    , output logic [DATA_W-1:0] o_rf_wr_data
    , output logic              o_rf_write
    , output logic              o_rf_enable
    , input  logic [DATA_W-1:0] i_rf_rd_data
    , input  logic              i_rf_error
);


endmodule : pt_axi4lite_bridge
