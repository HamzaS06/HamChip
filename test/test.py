# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import Timer


LOAD = 0b01
OUTPUT_ENABLE = 0b10


async def wait_us(duration=1):
    """Allow signals and gate-level delays to settle."""
    await Timer(duration, unit="us")


async def tick(dut):
    """One clock cycle with exactly one rising edge."""
    dut.clk.value = 0
    await wait_us(5)
    dut.clk.value = 1
    await wait_us(5)


def check_count(dut, expected):
    """Read the counter through its output-data port."""
    actual = int(dut.uio_out.value)
    assert actual == expected, (
        f"Expected count {expected}, got {actual}"
    )


def check_bus(dut, expected):
    """Read the simulated physical pins."""
    actual = int(dut.data_bus.value)
    assert actual == expected, (
        f"Expected bus {expected}, got {actual}"
    )


def check_high_impedance(dut):
    """All eight pins must be released."""
    actual = str(dut.data_bus.value).lower()
    assert actual == "zzzzzzzz", (
        f"Expected high impedance, got {actual}"
    )


@cocotb.test()
async def test_counter(dut):
    # Initial conditions: chip drives its output;
    # the external device is disconnected.
    dut.clk.value = 0
    dut.rst_n.value = 1
    dut.ena.value = 1
    dut.ui_in.value = OUTPUT_ENABLE
    dut.external_data.value = 0
    dut.external_oe.value = 0
    await wait_us()

    # 1. Reset without generating any clock edge.
    dut.rst_n.value = 0
    await wait_us()
    check_count(dut, 0)
    check_bus(dut, 0)

    # Reset must also hold the counter at zero.
    await tick(dut)
    check_count(dut, 0)

    dut.rst_n.value = 1
    await wait_us()

    # 2. Count through all 256 states, including overflow.
    for step in range(1, 257):
        await tick(dut)
        expected = step % 256
        check_count(dut, expected)
        check_bus(dut, expected)

    # Move to a nonzero value before testing reset again.
    for _ in range(7):
        await tick(dut)
    check_count(dut, 7)

    # 3. Asynchronous reset from a nonzero count.
    # Hold the clock low: no rising edge occurs.
    dut.clk.value = 0
    await wait_us()
    dut.rst_n.value = 0
    await wait_us()
    check_count(dut, 0)
    check_bus(dut, 0)

    dut.rst_n.value = 1
    await wait_us()
    await tick(dut)
    check_count(dut, 1)

    # 4. Disable output drivers while the clock is stopped.
    dut.clk.value = 0
    dut.ui_in.value = 0
    await wait_us()
    assert int(dut.uio_oe.value) == 0
    check_high_impedance(dut)
    check_count(dut, 1)

    # Counting continues while the output pins are released.
    await tick(dut)
    check_count(dut, 2)
    check_high_impedance(dut)

    # Enabling outputs reveals the current count immediately.
    dut.ui_in.value = OUTPUT_ENABLE
    await wait_us()
    assert int(dut.uio_oe.value) == 255
    check_bus(dut, 2)

    # 5. Test every possible programmable load value.
    expected = 2

    for value in range(256):
        # Disconnect the chip before driving the bus externally.
        dut.clk.value = 0
        dut.ui_in.value = 0
        await wait_us()

        dut.external_data.value = value
        dut.external_oe.value = 1
        dut.ui_in.value = LOAD
        await wait_us()

        # Load is synchronous: nothing changes before an edge.
        check_count(dut, expected)
        check_bus(dut, value)

        # Rising edge loads the external value.
        await tick(dut)
        check_count(dut, value)

        # Keep load asserted across another edge.
        # It must reload, rather than increment.
        await tick(dut)
        check_count(dut, value)

        # Release the external driver before enabling chip output.
        dut.ui_in.value = 0
        dut.external_oe.value = 0
        await wait_us()
        check_high_impedance(dut)

        dut.ui_in.value = OUTPUT_ENABLE
        await wait_us()
        check_bus(dut, value)

        # With load released, counting resumes.
        await tick(dut)
        expected = (value + 1) % 256
        check_count(dut, expected)
        check_bus(dut, expected)

    # 6. Reset must win when reset and load are both asserted.
    dut.clk.value = 0
    dut.ui_in.value = 0
    await wait_us()

    dut.external_data.value = 173
    dut.external_oe.value = 1
    dut.ui_in.value = LOAD
    await wait_us()

    dut.rst_n.value = 0
    await wait_us()
    check_count(dut, 0)

    await tick(dut)
    check_count(dut, 0)

    # Cleanly return to normal counting.
    dut.ui_in.value = 0
    dut.external_oe.value = 0
    await wait_us()

    dut.rst_n.value = 1
    dut.ui_in.value = OUTPUT_ENABLE
    await wait_us()
    check_bus(dut, 0)

    await tick(dut)
    check_count(dut, 1)
    check_bus(dut, 1)

    assert int(dut.uo_out.value) == 0
    dut._log.info("All counter checks passed")
