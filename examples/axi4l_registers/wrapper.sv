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

module wrapper
import   control_pkg::device_to_host_t
       , control_pkg::host_to_device_t
       , control_pkg::identity_t
       , control_pkg::reset_control_t
       , control_pkg::status_t
       , control_pkg::version_t;
#(
      parameter  ADDR_W = 32
    , parameter  DATA_W = 64
    , localparam STRB_W = DATA_W / 8
    , localparam PROT_W =  3
    , localparam RESP_W =  2
) (
      input  logic              i_clk
    , input  logic              i_rst
    // =========================================================================
    // AX4-Lite Upstream
    // =========================================================================
    , input  logic [ADDR_W-1:0] i_awaddr
    , input  logic [PROT_W-1:0] i_awprot
    , input  logic              i_awvalid
    , output logic              o_awready
    , input  logic [DATA_W-1:0] i_wdata
    , input  logic [STRB_W-1:0] i_wstrb
    , input  logic              i_wvalid
    , output logic              o_wready
    , output logic [RESP_W-1:0] o_bresp
    , output logic              o_bvalid
    , input  logic              i_bready
    , input  logic [ADDR_W-1:0] i_araddr
    , input  logic [PROT_W-1:0] i_arprot
    , input  logic              i_arvalid
    , output logic              o_arready
    , output logic [DATA_W-1:0] o_rdata
    , output logic [RESP_W-1:0] o_rresp
    , output logic              o_rvalid
    , input  logic              i_rready
    // =========================================================================
    // Internal Interfaces
    // =========================================================================
    , input  version_t        i_device_version_data
    , input  logic            i_device_version_strobe
    , input  status_t         i_device_status_data
    , input  logic            i_device_status_strobe
    , output reset_control_t  o_control_core_reset_0_data
    , output logic            o_control_core_reset_0_strobe
    , output reset_control_t  o_control_core_reset_1_data
    , output logic            o_control_core_reset_1_strobe
    , output reset_control_t  o_control_core_reset_2_data
    , output logic            o_control_core_reset_2_strobe
    , output reset_control_t  o_control_core_reset_3_data
    , output logic            o_control_core_reset_3_strobe
    , output host_to_device_t o_comms_0_h2d_data
    , output logic            o_comms_0_h2d_valid
    , input  logic            i_comms_0_h2d_ready
    , output logic [2:0]      o_comms_0_h2d_level
    , input  device_to_host_t i_comms_0_d2h_data
    , input  logic            i_comms_0_d2h_valid
    , output logic            o_comms_0_d2h_ready
    , output logic [2:0]      o_comms_0_d2h_level
    , output host_to_device_t o_comms_1_h2d_data
    , output logic            o_comms_1_h2d_valid
    , input  logic            i_comms_1_h2d_ready
    , output logic [2:0]      o_comms_1_h2d_level
    , input  device_to_host_t i_comms_1_d2h_data
    , input  logic            i_comms_1_d2h_valid
    , output logic            o_comms_1_d2h_ready
    , output logic [2:0]      o_comms_1_d2h_level
);

logic [       6:0] rf_address;
logic [DATA_W-1:0] rf_wr_data, rf_rd_data;
logic              rf_write, rf_enable, rf_error;

pt_axi4lite_bridge #(
      .AXI_ADDR_W   ( ADDR_W     )
    , .RF_ADDR_W    ( 7          )
    , .DATA_W       ( DATA_W     )
) u_bridge (
      .i_clk        ( i_clk      )
    , .i_rst        ( i_rst      )
    // =========================================================================
    // AX4-Lite Upstream
    // =========================================================================
    , .i_awaddr     ( i_awaddr   )
    , .i_awprot     ( i_awprot   )
    , .i_awvalid    ( i_awvalid  )
    , .o_awready    ( o_awready  )
    , .i_wdata      ( i_wdata    )
    , .i_wstrb      ( i_wstrb    )
    , .i_wvalid     ( i_wvalid   )
    , .o_wready     ( o_wready   )
    , .o_bresp      ( o_bresp    )
    , .o_bvalid     ( o_bvalid   )
    , .i_bready     ( i_bready   )
    , .i_araddr     ( i_araddr   )
    , .i_arprot     ( i_arprot   )
    , .i_arvalid    ( i_arvalid  )
    , .o_arready    ( o_arready  )
    , .o_rdata      ( o_rdata    )
    , .o_rresp      ( o_rresp    )
    , .o_rvalid     ( o_rvalid   )
    , .i_rready     ( i_rready   )
    // =========================================================================
    // Register Interface Downstream
    // =========================================================================
    , .o_rf_address ( rf_address )
    , .o_rf_wr_data ( rf_wr_data )
    , .o_rf_write   ( rf_write   )
    , .o_rf_enable  ( rf_enable  )
    , .i_rf_rd_data ( rf_rd_data )
    , .i_rf_error   ( rf_error   )
);

control_rf u_rf (
      .i_clk                         ( i_clk                         )
    , .i_rst                         ( i_rst                         )
    // =========================================================================
    // External Interface (driven by bridge)
    // =========================================================================
    , .i_address                     ( rf_address                    )
    , .i_wr_data                     ( rf_wr_data                    )
    , .i_write                       ( rf_write                      )
    , .i_enable                      ( rf_enable                     )
    , .o_rd_data                     ( rf_rd_data                    )
    , .o_error                       ( rf_error                      )
    // =========================================================================
    // Internal Interfaces
    // =========================================================================
    , .i_device_version_data         ( i_device_version_data         )
    , .i_device_version_strobe       ( i_device_version_strobe       )
    , .i_device_status_data          ( i_device_status_data          )
    , .i_device_status_strobe        ( i_device_status_strobe        )
    , .o_control_core_reset_0_data   ( o_control_core_reset_0_data   )
    , .o_control_core_reset_0_strobe ( o_control_core_reset_0_strobe )
    , .o_control_core_reset_1_data   ( o_control_core_reset_1_data   )
    , .o_control_core_reset_1_strobe ( o_control_core_reset_1_strobe )
    , .o_control_core_reset_2_data   ( o_control_core_reset_2_data   )
    , .o_control_core_reset_2_strobe ( o_control_core_reset_2_strobe )
    , .o_control_core_reset_3_data   ( o_control_core_reset_3_data   )
    , .o_control_core_reset_3_strobe ( o_control_core_reset_3_strobe )
    , .o_comms_0_h2d_data            ( o_comms_0_h2d_data            )
    , .o_comms_0_h2d_valid           ( o_comms_0_h2d_valid           )
    , .i_comms_0_h2d_ready           ( i_comms_0_h2d_ready           )
    , .o_comms_0_h2d_level           ( o_comms_0_h2d_level           )
    , .i_comms_0_d2h_data            ( i_comms_0_d2h_data            )
    , .i_comms_0_d2h_valid           ( i_comms_0_d2h_valid           )
    , .o_comms_0_d2h_ready           ( o_comms_0_d2h_ready           )
    , .o_comms_0_d2h_level           ( o_comms_0_d2h_level           )
    , .o_comms_1_h2d_data            ( o_comms_1_h2d_data            )
    , .o_comms_1_h2d_valid           ( o_comms_1_h2d_valid           )
    , .i_comms_1_h2d_ready           ( i_comms_1_h2d_ready           )
    , .o_comms_1_h2d_level           ( o_comms_1_h2d_level           )
    , .i_comms_1_d2h_data            ( i_comms_1_d2h_data            )
    , .i_comms_1_d2h_valid           ( i_comms_1_d2h_valid           )
    , .o_comms_1_d2h_ready           ( o_comms_1_d2h_ready           )
    , .o_comms_1_d2h_level           ( o_comms_1_d2h_level           )
);

endmodule : wrapper
