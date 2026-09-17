<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This design implements an 8-bit unsigned up counter.

The counter increments on each rising clock edge and wraps from
255 to 0.

The active-low reset, rst_n, is asynchronous. Asserting reset
clears the counter immediately without requiring a clock edge.

When LOAD is high, the next rising clock edge loads the value
present on the eight DATA pins instead of incrementing.

Priority is:
1. Asynchronous reset.
2. Synchronous load.
3. Increment.

The DATA pins form a shared bidirectional bus. OUTPUT_ENABLE
controls all eight output drivers:

- OUTPUT_ENABLE = 1: the chip drives the current count.
- OUTPUT_ENABLE = 0: the chip releases the pins to high impedance.

Disabling the outputs does not stop the counter.

## Pin assignments

| Signal | Function |
| --- | --- |
| clk | Rising-edge clock |
| rst_n | Asynchronous active-low reset |
| ui_in[0] | LOAD |
| ui_in[1] | OUTPUT_ENABLE |
| uio[7:0] | Shared load-input and counter-output DATA bus |

Other dedicated inputs are unused.
Dedicated outputs are tied to zero.

## How to use

### Reset

Drive rst_n low to clear the count.
Release rst_n high to allow loading or counting.

### Count

Set LOAD low and OUTPUT_ENABLE high.
Each rising clock edge increments the displayed count.

### Load a starting value

1. Set OUTPUT_ENABLE low to release the DATA pins.
2. Drive the desired 8-bit value onto DATA externally.
3. Set LOAD high.
4. Apply a rising clock edge.
5. Set LOAD low.
6. Disconnect the external DATA driver.
7. Set OUTPUT_ENABLE high to read the loaded value.

Do not drive DATA externally while the chip output drivers
are enabled.

### Tri-state output

Set OUTPUT_ENABLE low and disconnect any external driver.
The DATA pins then become high impedance.

## How to test

The Cocotb test in test/test.py checks:

- Reset without a rising clock edge.
- Reset while the count is nonzero.
- Holding reset active across clock edges.
- Counting through a complete 256-cycle sequence.
- Overflow from 255 to 0.
- Loading every value from 0 to 255.
- No load before the rising edge.
- Holding LOAD active across multiple edges.
- Resuming counting after loading.
- Reset taking priority over load.
- Output enable and high-impedance behavior.
- Continued counting while outputs are disabled.

The testbench models the physical tri-state bus as data_bus.
Inspect data_bus in the waveform to observe high impedance.

With the simulator and Python dependencies installed, run
the following commands from the repository root:

    cd test
    make -B

Alternatively, commit the files and inspect the GitHub Actions
test and gds workflows.

## External hardware

No external hardware is needed for simulation.

A hardware demonstration requires a clock source, reset and
control signals, and an external driver for programmable load
values. The external driver must release the DATA bus before
the chip output drivers are enabled.
