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
import math
base_types  = {x for x in baseline._pt_references() if x._PT_BASE is Register}
widest_type = max(len(tc.snake_case(x.__name__)) for x in base_types) + 2
pipelining  = options.get("pipelining", 1)
primaries   = list(filter(lambda x: x._PT_BEHAVIOUR.is_primary, baseline))
%>\

module ${type(baseline).__name__ | tc.snake_case}_rf
import   ${type(baseline).__name__ | tc.snake_case}_pkg::offset_t\
%for foreign in baseline._pt_foreign():

    %if foreign._PT_ATTACHED_TO:
<%      refers_to = foreign._PT_ATTACHED_TO._pt_lookup(foreign) %>\
       , ${foreign._PT_ATTACHED_TO._pt_name() | tc.snake_case}::${refers_to | tc.snake_case}_t\
    %else:
       , ${foreign._PT_ATTACHED_TO._pt_name() | tc.snake_case}::${foreign._pt_name() | tc.snake_case}_t\
    %endif
%endfor ## foreign in baseline._pt_foreign()
%for reg in baseline:

       , ${type(baseline).__name__ | tc.snake_case}_pkg::${reg._pt_fullname.upper() | tc.underscore}_OFFSET\
%endfor ## reg in baseline
%for idx, base in enumerate(sorted(base_types, key=lambda x: x.__name__)):

       , ${type(baseline).__name__ | tc.snake_case}_pkg::${base.__name__ | tc.snake_case}_t\
%endfor ## idx, base in enumerate(sorted(base_types, key=lambda x: x.__name__))
;
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
// Typedefs
// =============================================================================

typedef logic [DATA_W-1:0] _pt_rf_data_t;

// =============================================================================
// Access Handling
// =============================================================================

logic is_read, is_write;

assign is_read  = i_enable && !i_write;
assign is_write = i_enable &&  i_write;

%for reg in primaries:
<%
    behav  = reg._PT_BEHAVIOUR
    struct = tc.snake_case(type(reg).__name__) + "_t"
    rname  = tc.underscore(reg._pt_fullname)
%>\
// =============================================================================
// Register: ${reg._pt_fullname} (${behav.name})
// =============================================================================
    %if behav is Behaviour.CONSTANT:

${struct} current_${rname};
logic error_${rname}, is_write_${rname};

assign is_write_${rname} = is_write && (i_address == ${rname.upper()}_OFFSET);
assign error_${rname}    = is_write_${rname};

assign current_${rname} = '{
        %for idx, (field, fname) in enumerate(reg._pt_fields.items()):
    ${"," if idx > 0 else " "} ${fname}: ${int(field._pt_width)}'h${f"{int(field):X}"}
        %endfor ## field, fname in reg._pt_fields.items()
};

    %elif behav is Behaviour.DATA_X2I:

${struct} reset_${rname}, current_${rname};
logic error_${rname}, is_write_${rname}, strobe_${rname};

assign is_write_${rname} = is_write && (i_address == ${rname.upper()}_OFFSET);
assign error_${rname}    = 1'b0;

assign reset_${rname} = '{
        %for idx, (field, fname) in enumerate(reg._pt_fields.items()):
    ${"," if idx > 0 else " "} ${fname}: \
            %if field._PT_BASE in (Enum, Struct, Union):
${type(field).__name__ | tc.snake_case}_t'(${int(field._pt_width)}'h${f"{int(field):X}"})
            %else:
${field._pt_width}'h${f"{int(field):X}"}
            %endif
        %endfor ## field, fname in reg._pt_fields.items()
};

always_ff @(posedge i_clk, posedge i_rst) begin : ff_${rname}
    if (i_rst) begin
        current_${rname} <= reset_${rname};
        strobe_${rname}  <= 1'b0;
    end else begin
        if (is_write_${rname}) begin
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

${struct} reset_${rname}, current_${rname}, buffer_${rname};
logic error_${rname}, is_write_${rname};

assign is_write_${rname} = is_write && (i_address == ${rname.upper()}_OFFSET);
assign error_${rname}    = is_write_${rname};

assign reset_${rname} = '{
        %for idx, (field, fname) in enumerate(reg._pt_fields.items()):
    ${"," if idx > 0 else " "} ${fname}: \
            %if field._PT_BASE in (Enum, Struct, Union):
${type(field).__name__ | tc.snake_case}_t'(${int(field._pt_width)}'h${f"{int(field):X}"})
            %else:
${int(field._pt_width)}'h${f"{int(field):X}"}
            %endif
        %endfor ## field, fname in reg._pt_fields.items()
};

always_ff @(posedge i_clk, posedge i_rst) begin : ff_${rname}
    if (i_rst)
        buffer_${rname} <= reset_${rname};
    else if (i_${rname}_strobe)
        buffer_${rname} <= i_${rname}_data;
end

assign current_${rname} = '{
        %for idx, (field, fname) in enumerate(reg._pt_fields.items()):
    ${',' if idx else ' '} ${fname}: \
            %if isinstance(field, Constant):
${int(field._pt_width)}'h${f"{int(field):X}"}
            %else:
buffer_${rname}.${fname}
            %endif ## isinstance(field, Constant)
        %endfor ## idx, (field, fname) in enumerate(reg._pt_fields.items())
};

    %if len([x for x in reg._pt_fields.keys() if isinstance(x, Constant)]):
logic _unused_${rname} = &{
      1'b0
            %for field, fname in reg._pt_fields.items():
                %if isinstance(field, Constant):
    , buffer_${rname}.${fname}
                %endif ## isinstance(field, Constant)
            %endfor ## field, fname in reg._pt_fields.items()
};

    %endif
    %elif behav is Behaviour.FIFO_X2I:

logic error_${rname}, is_read_${rname}, is_write_${rname}, is_full_${rname};
logic [${reg._pt_paired[Behaviour.LEVEL]._pt_width-1}:0] level_${rname};

assign is_read_${rname}  = is_read && (i_address == ${rname.upper()}_OFFSET);
assign is_write_${rname} = is_write && (i_address == ${rname.upper()}_OFFSET);
assign error_${rname}    = is_read_${rname} || (is_write_${rname} && is_full_${rname});

pt_fifo #(
      .DATA_T     ( ${struct} )
    , .DEPTH      ( ${reg._PT_DEPTH} )
) u_${rname}_fifo (
      .i_clk      ( i_clk )
    , .i_rst      ( i_rst )
    // Push stream
    , .i_wr_data  ( ${struct}'(i_wr_data) )
    , .i_wr_valid ( is_write_${rname} )
    , .o_wr_ready ( )
    // Pop stream
    , .o_rd_data  ( o_${rname}_data  )
    , .o_rd_valid ( o_${rname}_valid )
    , .i_rd_ready ( i_${rname}_ready )
    // Status
    , .o_level    ( level_${rname} )
    , .o_full     ( is_full_${rname} )
    , .o_hwm      ( )
    , .o_empty    ( )
);

    %elif behav is Behaviour.FIFO_I2X:

${struct} current_${rname};
logic error_${rname}, is_read_${rname}, is_write_${rname}, rd_valid_${rname};
logic [${reg._pt_paired[Behaviour.LEVEL]._pt_width-1}:0] level_${rname};

assign is_read_${rname}  = is_read && (i_address == ${rname.upper()}_OFFSET);
assign is_write_${rname} = is_write && (i_address == ${rname.upper()}_OFFSET);
assign error_${rname}    = is_write_${rname} || (is_read_${rname} && !rd_valid_${rname});

pt_fifo #(
      .DATA_T     ( ${struct} )
    , .DEPTH      ( ${reg._PT_DEPTH} )
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
    , .i_rd_ready ( is_read_${rname}  )
    // Status
    , .o_level    ( level_${rname} )
    , .o_full     ( )
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
<%
# Determine the fan-in rate required across the available pipelining (i.e. how
# many entries will fan into a mux at each stage)
per_mux = int(math.ceil(len(primaries) ** (1 / pipelining)))

# Split registers into muxes at the first stage
muxes = []
which_mux = {}
for entry in primaries:
    # Get the mux to append into
    if len(muxes) == 0 or len(muxes[-1]) >= per_mux:
        muxes.append([])
    # Append register into the last mux
    muxes[-1].append(entry)
    which_mux[entry] = len(muxes) - 1
%>\

// Register access handling
localparam NUM_MUXES_0 = ${len(muxes)};
_pt_rf_data_t read_data [NUM_MUXES_0-1:0];
logic [NUM_MUXES_0-1:0] active, error;

always_comb begin : comb_access
    for (int idx = 0; idx < NUM_MUXES_0; idx++) read_data[idx] = _pt_rf_data_t'(0);
    active = NUM_MUXES_0'(0);
    error = NUM_MUXES_0'(0);

    case (i_address)
%for reg in primaries:
<%  mux_idx = which_mux[reg] %>\
        ${reg._pt_fullname.upper() | tc.underscore}_OFFSET: begin
            active[${mux_idx}] = 1'b1;
    %if reg._PT_BEHAVIOUR.external_read:
            read_data[${mux_idx}] = DATA_W'(current_${reg._pt_fullname | tc.underscore});
    %else:
            read_data[${mux_idx}] = DATA_W'(0);
    %endif
            error[${mux_idx}] = error_${reg._pt_fullname | tc.underscore};
        end
    %for behav, sub in reg._pt_paired.items():
        ${sub._pt_fullname.upper() | tc.underscore}_OFFSET: begin
            active[${mux_idx}] = 1'b1;
        %if behav is Behaviour.LEVEL:
            read_data[${mux_idx}] = DATA_W'(level_${reg._pt_fullname | tc.underscore});
            error[${mux_idx}] = is_write;
        %endif
        end
    %endfor ## behav, sub in reg._pt_paired.items()
%endfor ## reg in baseline
        // If no other channel has responded, flag an error
        default: begin
            active = NUM_MUXES_0'(1);
            error = {NUM_MUXES_0{1'b1}};
        end
    endcase
end

// Pipeling stage 0
_pt_rf_data_t read_pipe_0_q [NUM_MUXES_0-1:0];
logic [NUM_MUXES_0-1:0] active_pipe_0_q, error_pipe_0_q;

always_ff @(posedge i_clk, posedge i_rst) begin : ff_pipe_0
    if (i_rst) begin
        for (int idx = 0; idx < NUM_MUXES_0; idx++) read_pipe_0_q[idx] <= _pt_rf_data_t'(0);
        active_pipe_0_q <= NUM_MUXES_0'(0);
        error_pipe_0_q <= NUM_MUXES_0'(0);
    end else begin
        for (int idx = 0; idx < NUM_MUXES_0; idx++) read_pipe_0_q[idx] <= read_data[idx];
        active_pipe_0_q <= active;
        error_pipe_0_q <= error;
    end
end

<% prev_muxes = len(muxes) %>\
%for idx_pipe in range(1, pipelining):
<%
    # Figure out number of muxes in this pipelining stage (round up)
    num_muxes = ((prev_muxes + per_mux - 1) // per_mux)
%>\
// Pipeling stage ${idx_pipe}
localparam NUM_MUXES_${idx_pipe} = ${num_muxes};

_pt_rf_data_t read_pipe_${idx_pipe}_d [NUM_MUXES_${idx_pipe}-1:0];
_pt_rf_data_t read_pipe_${idx_pipe}_q [NUM_MUXES_${idx_pipe}-1:0];
logic [${num_muxes-1}:0] active_pipe_${idx_pipe}_d, active_pipe_${idx_pipe}_q,
      error_pipe_${idx_pipe}_d, error_pipe_${idx_pipe}_q;

always_comb begin : comb_pipe_${idx_pipe}
    for (int idx = 0; idx < NUM_MUXES_${idx_pipe}; idx++) read_pipe_${idx_pipe}_d[idx] = _pt_rf_data_t'(0);
    active_pipe_${idx_pipe}_d = NUM_MUXES_${idx_pipe}'(0);
    error_pipe_${idx_pipe}_d = NUM_MUXES_${idx_pipe}'(0);

    unique case (active_pipe_${idx_pipe-1}_q)
    %for idx_prev_mux in range(prev_muxes):
<%      idx_curr_mux = idx_prev_mux // per_mux %>\
        ${prev_muxes}'b${f"{1 << idx_prev_mux:0{prev_muxes}b}"}: begin
            active_pipe_${idx_pipe}_d[${idx_curr_mux}] = 1'b1;
            read_pipe_${idx_pipe}_d[${idx_curr_mux}] = read_pipe_${idx_pipe-1}_q[${idx_prev_mux}];
            error_pipe_${idx_pipe}_d[${idx_curr_mux}] = error_pipe_${idx_pipe-1}_q[${idx_prev_mux}];
        end
    %endfor ## idx_prev_mux in range(prev_muxes)
        default: begin
            active_pipe_${idx_pipe}_d = NUM_MUXES_${idx_pipe}'(1);
            error_pipe_${idx_pipe}_d = {NUM_MUXES_${idx_pipe}{|error_pipe_${idx_pipe-1}_q}};
        end
    endcase
end

always_ff @(posedge i_clk, posedge i_rst) begin : ff_pipe_${idx_pipe}
    if (i_rst) begin
        for (int idx = 0; idx < NUM_MUXES_${idx_pipe}; idx++) read_pipe_${idx_pipe}_q[idx] <= _pt_rf_data_t'(0);
        active_pipe_${idx_pipe}_q <= NUM_MUXES_${idx_pipe}'(0);
        error_pipe_${idx_pipe}_q <= NUM_MUXES_${idx_pipe}'(0);
    end else begin
        for (int idx = 0; idx < NUM_MUXES_${idx_pipe}; idx++) read_pipe_${idx_pipe}_q[idx] <= read_pipe_${idx_pipe}_d[idx];
        active_pipe_${idx_pipe}_q <= active_pipe_${idx_pipe}_d;
        error_pipe_${idx_pipe}_q <= error_pipe_${idx_pipe}_d;
    end
end

<%
    # Remember how many muxes were in the previous stage
    prev_muxes = num_muxes
%>\
%endfor ## idx in range(1, pipelining)
// Drive outputs
assign o_rd_data = read_pipe_${pipelining-1}_q[0];
assign o_error   = |{active_pipe_${pipelining-1}_q[0] & error_pipe_${pipelining-1}_q[0]};

endmodule : ${type(baseline).__name__ | tc.snake_case}_rf
