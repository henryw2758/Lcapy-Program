"""Test fixtures for netlist-to-text."""

import pytest
from netlist_to_text.circuit import Circuit


def test_voltage_divider_fixture():
    """Test using the voltage divider fixture."""
    cct = Circuit()
    cct.from_netlist_file("fixtures/voltage_divider.net")
    
    assert len(cct.elements) == 3
    assert "voltage source" in cct.generate_description()
    assert "10 Volt" in cct.generate_description()


def test_parallel_resistors_fixture():
    """Test using the parallel resistors fixture."""
    cct = Circuit()
    cct.from_netlist_file("fixtures/parallel_resistors.net")
    
    assert len(cct.elements) == 2
    desc = cct.generate_description()
    assert "parallel" in desc


def test_series_rc_fixture():
    """Test using the series RC fixture."""
    cct = Circuit()
    cct.from_netlist_file("fixtures/series_rc.net")
    
    assert len(cct.elements) == 3
    desc = cct.generate_description()
    assert "inductor" not in desc  # No inductor in this circuit
    assert "capacitor" in desc
    assert "resistor" in desc
