`default_nettype none
`timescale 1ns / 1ps

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  // Dump the signals to a FST file. You can view it with gtkwave or surfer.
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tb);
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;


// Simulated physical bidirectional pins.
    tri [7:0] data_bus;

    // External device supplying the load value.
    reg [7:0] external_data;
    reg external_oe;

    assign data_bus = external_oe
                    ? external_data
                    : 8'bzzzzzzzz;

    // Model the chip's eight physical output drivers.
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : output_drivers
            assign data_bus[i] = uio_oe[i]
                               ? uio_out[i]
                               : 1'bz;
        end
    endgenerate

    // The input path reads the physical bus.
    assign uio_in = data_bus;

`ifdef GL_TEST
    wire VPWR = 1'b1;
    wire VGND = 1'b0;
`endif

    tt_um_hamzas06_counter user_project (
`ifdef GL_TEST
        .VPWR   (VPWR),
        .VGND   (VGND),
`endif
        .ui_in  (ui_in),
        .uo_out (uo_out),
        .uio_in (uio_in),
        .uio_out(uio_out),
        .uio_oe (uio_oe),
        .ena    (ena),
        .clk    (clk),
        .rst_n  (rst_n)
    );

endmodule

`default_nettype wire
