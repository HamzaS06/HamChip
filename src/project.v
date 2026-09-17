/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hamzas06_counter  (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Control inputs:
    // ui_in[0] = load
    // ui_in[1] = output enable
    wire load;
    wire output_enable;

    assign load          = ui_in[0];
    assign output_enable = ui_in[1];

    // Eight flip-flops store a number from 0 to 255.
    reg [7:0] count;

    // Asynchronous active-low reset.
    // Loading and counting happen on rising clock edges.
    // Priority: reset > load > count.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            count <= 8'd0;
        else if (load)
            count <= uio_in;
        else
            count <= count + 8'd1;
    end

    // Counter data goes to the bidirectional output drivers.
    assign uio_out = count;

    // Enable all eight output drivers together.
    // 1: drive the count onto the pins.
    // 0: release the pins into high impedance.
    assign uio_oe = {8{output_enable}};

    // Dedicated output pins are unused.
    assign uo_out = 8'b0;

    // Mark unused inputs for the lint tools.
    wire _unused = &{ena, ui_in[7:2], 1'b0};

endmodule

`default_nettype wire
