<%doc>
Copyright 2023, Peter Birch, mailto:peter@intuity.io

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
</%doc>\
<%include file="header.mako" args="delim='//'" />\
<%namespace name="blocks" file="blocks.mako" />\
<%
base_types  = {x for x in baseline._pt_references() if x._PT_BASE is Register}
widest_type = max(len(tc.snake_case(x.__name__)) for x in base_types) + 2
%>\

`include "pt_common.svh"

module ${type(baseline).__name__ | tc.snake_case}_rf
import   ${type(baseline).__name__ | tc.snake_case}::offset_t
%for base in sorted(base_types, key=lambda x: x.__name__):
       , ${type(baseline).__name__ | tc.snake_case}_pkg::${base.__name__ | tc.snake_case}_t;
%endfor ## base in sorted(base_types, key=lambda x: x.__name__)
#(
      ## TODO @intuity: Use the cadence width, not the raw width
      localparam DATA_W = ${baseline._PT_BIT_CADENCE}
) (
    // =========================================================================
    // External Interface (driven by bridge)
    // =========================================================================
    ## TODO @intuity: Consider supporting byte strobed writes?
      input  logic              i_clk
    , input  logic              i_rst
    , input  offset_t           i_address
    , input  logic [DATA_W-1:0] i_wr_data
    , input  logic              i_write
    , input  logic              i_enable
    , output logic [DATA_W-1:0] o_rd_data
    , output logic              o_error
    // =========================================================================
    // Internal Interfaces
    // =========================================================================
%for reg in baseline:
<%
    struct = tc.snake_case(type(reg).__name__) + "_t"
    rname  = tc.underscore(reg._pt_fullname)
%>\
    %if reg._PT_BEHAVIOUR.internal_read:
    , output ${f"{struct:{widest_type}}"} o_${rname}_data
        %if reg._PT_BEHAVIOUR.internal_read_stream:
    , output ${f"{'logic':{widest_type}}"} o_${rname}_valid
    , input  ${f"{'logic':{widest_type}}"} i_${rname}_ready
        %elif reg._PT_BEHAVIOUR.internal_read_strobe:
    , output ${f"{'logic':{widest_type}}"} o_${rname}_strobe
        %endif
    %elif reg._PT_BEHAVIOUR.internal_write:
    , input  ${f"{struct:{widest_type}}"} i_${rname}_data
        %if reg._PT_BEHAVIOUR.internal_write_stream:
    , input  ${f"{'logic':{widest_type}}"} i_${rname}_valid
    , output ${f"{'logic':{widest_type}}"} o_${rname}_ready
        %elif reg._PT_BEHAVIOUR.internal_write_strobe:
    , input  ${f"{'logic':{widest_type}}"} i_${rname}_strobe
        %endif
    %endif
    %for behav, sub in reg._pt_paired.items():
        %if behav is Behaviour.LEVEL:
    , output ${f"{'logic ['+str(sub.value._pt_width-1)+':0]':{widest_type}}"} o_${sub._pt_fullname | tc.underscore}
        %endif ## behav is Behaviour.LEVEL
    %endfor ## sub in reg._pt_paired.items()
%endfor ## reg in baseline
);

// =============================================================================
// Access Handling
// =============================================================================

logic is_read, is_write;

assign is_read  = i_enable && !i_write;
assign is_write = i_enable &&  i_write;

%for reg in filter(lambda x: x._PT_BEHAVIOUR.is_primary, baseline):
<%
behav  = reg._PT_BEHAVIOUR
struct = tc.snake_case(type(reg).__name__) + "_t"
rname  = tc.underscore(reg._pt_fullname)
%>\
// =============================================================================
// Register: ${reg._pt_fullname} (${behav.name})
// =============================================================================

${struct} current_${rname};
logic is_read_${rname}, is_write_${rname}, error_${rname};

assign is_read_${rname} = is_read && (i_address == ${rname.upper()}_OFFSET);
assign is_write_${rname} = is_write && (i_address == ${rname.upper()}_OFFSET);
%if behav is Behaviour.CONSTANT:
assign current_${rname} = '{
%for idx, (field, fname) in enumerate(reg._pt_fields.items()):
    ${"," if idx > 0 else " "} ${fname}: ${field._pt_width}'h${f"{int(field):X}"}
%endfor ## field, fname in reg._pt_fields.items()
};
%elif behav is Behaviour.DATA_X2I:
assign error_${rname} = 1'b0;

logic strobe_${rname};

always_ff @(posedge i_clk, posedge i_rst) begin : ff_${fname}
    ## TODO @intuity: Handle non-zero reset value?
    if (i_rst) begin
        current_${rname} <= ${struct}'(0);
        strobe_${rname}  <= 1'b0;
    end else begin
        if (is_write && i_address == ${rname.upper()}_OFFSET) begin
            current_${rname} <= ${struct}'(i_wr_data);
            strobe_${rname}  <= 1'b1;
        end else begin
            strobe_${rname}  <= 1'b0;
        end
    end
end

assign o_${rname}_data   = current_${rname};
assign o_${rname}_strobe = strobe_${rname};

%elif behav is Behaviour.DATA_I2X:
assign error_${rname} = is_write_${rname};

always_ff @(posedge i_clk, posedge i_rst) begin : ff_${fname}
    ## TODO @intuity: Handle non-zero reset value?
    if (i_rst)
        current_${rname} <= ${struct}'(0);
    else if (i_${rname}_strobe)
        current_${rname} <= i_${rname}_data;
end
%elif behav is Behaviour.FIFO_X2I:
assign error_${rname} = is_read_${rname};

logic       wr_ready_${rname};
logic [2:0] level_${rname};

## TODO @intuity: Allow depth to be controlled
pt_fifo #(
      .DATA_T     ( ${struct} )
    , .DEPTH      ( 4 )
) u_${rname}_fifo (
      .i_clk      ( i_clk )
    , .i_rst      ( i_rst )
    // Push stream
    , .i_wr_data  ( ${struct}'(i_wr_data) )
    , .i_wr_valid ( is_write_${rname} )
    , .o_wr_ready ( wr_ready_${rname} )
    // Pop stream
    , .o_rd_data  ( o_${rname}_data  )
    , .o_rd_valid ( o_${rname}_valid )
    , .i_rd_ready ( i_${rname}_ready )
    // Status
    , .o_level    ( level_${rname} )
    , .o_full     ( )
    , .o_hwm      ( )
    , .o_empty    ( )
);
%elif behav is Behaviour.FIFO_I2X:
assign error_${rname} = is_write_${rname};

logic       rd_valid_${rname},
            rd_ready_${rname},
            is_full_${rname},
            is_empty_${rname},
            error_${rname};
logic [2:0] level_${rname};

pt_fifo #(
      .DATA_T     ( ${struct} )
    , .DEPTH      ( 4 )
) u_${rname}_fifo (
      .i_clk      ( i_clk )
    , .i_rst      ( i_rst )
    // Push stream
    , .i_wr_data  ( i_${rname}_data  )
    , .i_wr_valid ( i_${rname}_valid )
    , .o_wr_ready ( o_${rname}_ready )
    // Pop stream
    , .o_rd_data  ( current_${rname}  )
    , .o_rd_valid ( rd_valid_${rname} )
    , .i_rd_ready ( rd_ready_${rname} )
    // Status
    , .o_level    ( level_${rname}   )
    , .o_full     ( is_full_${rname} )
    , .o_hwm      ( )
    , .o_empty    ( )
);
%else:
<%  raise NotImplementedError() %>\
%endif
%for behav, sub in reg._pt_paired.items():
    %if behav is Behaviour.LEVEL:
assign o_${sub._pt_fullname | tc.underscore} = level_${rname};
    %endif ## behav is Behaviour.LEVEL
%endfor ## sub in reg._pt_paired.items()

%endfor ## reg in baseline
// =============================================================================
// Access Response
// =============================================================================

logic [DATA_W-1:0] read_data_d, read_data_q;
logic              error_d, error_q;

assign o_rd_data = read_data_q;
assign o_error   = error_q;

always_comb begin : comb_access
    read_data_d = read_data_q;
    error_d     = error_q;
    case (i_address)
%for reg in filter(lambda x: x._PT_BEHAVIOUR.is_primary, baseline):
        ${reg._pt_fullname.upper() | tc.underscore}_OFFSET: begin
            read_data_d = current_${reg._pt_fullname | tc.underscore};
            error_d     = error_${reg._pt_fullname | tc.underscore};
        end
    %for behav, sub in reg._pt_paired.items():
        ${sub._pt_fullname.upper() | tc.underscore}_OFFSET: begin
        %if behav is Behaviour.LEVEL:
            read_data_d = level_${reg._pt_fullname | tc.underscore};
            error_d     = is_write;
        %endif
        end
    %endfor ## behav, sub in reg._pt_paired.items()
%endfor ## reg in baseline
        default: begin
            read_data_d = DATA_W'(0);
            error_d     = 1'b1;
        end
    endcase
end

endmodule : ${type(baseline).__name__ | tc.snake_case}_rf
