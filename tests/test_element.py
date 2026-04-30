"""Tests for the element module."""

import pytest
from netlist_to_text.element import Element


class TestElementCreation:
    """Test element creation and basic properties."""

    def test_basic_resistor(self):
        """Test creating a basic resistor."""
        elem = Element("R1", "N001", "N002", "1k")
        assert elem.name == "R1"
        assert elem.first_node == "node 1"
        assert elem.second_node == "node 2"
        assert elem.value == "1k"

    def test_ground_node(self):
        """Test conversion of node '0' to 'ground'."""
        elem = Element("R1", "0", "N001", "1k")
        assert elem.first_node == "ground"
        assert elem.second_node == "node 1"

    def test_node_numbering(self):
        """Test conversion of N-prefixed nodes."""
        elem = Element("C1", "N005", "N010", "1u")
        assert elem.first_node == "node 5"
        assert elem.second_node == "node 10"

    def test_plain_node_numbers(self):
        """Test handling of plain node numbers."""
        elem = Element("L1", "1", "2", "10m")
        assert elem.first_node == "node 1"
        assert elem.second_node == "node 2"

    def test_lcapy_underscore_notation(self):
        """Test handling of Lcapy's underscore notation for wire routing."""
        # Ground with underscore suffix
        elem = Element("R1", "0_1", "1", "1k")
        assert elem.first_node == "ground"
        assert elem.second_node == "node 1"

        # Node 1 with underscore suffix
        elem = Element("R2", "1_1", "2", "2k")
        assert elem.first_node == "node 1"
        assert elem.second_node == "node 2"

        # Node 2 with underscore suffix
        elem = Element("R3", "2", "2_1", "3k")
        assert elem.first_node == "node 2"
        assert elem.second_node == "node 2"

        # N-prefixed nodes with underscore
        elem = Element("R4", "N001_1", "N002", "4k")
        assert elem.first_node == "node 1"
        assert elem.second_node == "node 2"


class TestElementTypeDetection:
    """Test element type detection."""

    def test_resistor_type(self):
        """Test resistor type detection."""
        elem = Element("R1", "0", "1", "1k")
        assert elem.get_element_type() == "resistor"

    def test_inductor_type(self):
        """Test inductor type detection."""
        elem = Element("L1", "0", "1", "1m")
        assert elem.get_element_type() == "inductor"

    def test_capacitor_type(self):
        """Test capacitor type detection."""
        elem = Element("C1", "0", "1", "1u")
        assert elem.get_element_type() == "capacitor"

    def test_voltage_source_type(self):
        """Test voltage source type detection."""
        elem = Element("V1", "0", "1", "10")
        assert elem.get_element_type() == "voltage source"

    def test_current_source_type(self):
        """Test current source type detection."""
        elem = Element("I1", "0", "1", "1")
        assert elem.get_element_type() == "current source"

    def test_conductance_type(self):
        """Test conductance type detection."""
        elem = Element("G1", "0", "1", "1")
        assert elem.get_element_type() == "conductance"

    def test_type_with_custom_name(self):
        """Test type detection with custom name parameter."""
        elem = Element("R1", "0", "1", "1k")
        assert elem.get_element_type("V2") == "voltage source"
        assert elem.get_element_type("L5") == "inductor"


class TestElementUnits:
    """Test element unit detection."""

    def test_resistor_unit(self):
        """Test resistor unit."""
        elem = Element("R1", "0", "1", "1k")
        assert elem.get_element_unit() == "Ohm"

    def test_inductor_unit(self):
        """Test inductor unit."""
        elem = Element("L1", "0", "1", "1m")
        assert elem.get_element_unit() == "Henry"

    def test_capacitor_unit(self):
        """Test capacitor unit."""
        elem = Element("C1", "0", "1", "1u")
        assert elem.get_element_unit() == "Farad"

    def test_voltage_unit(self):
        """Test voltage source unit."""
        elem = Element("V1", "0", "1", "10")
        assert elem.get_element_unit() == "Volt"

    def test_current_unit(self):
        """Test current source unit."""
        elem = Element("I1", "0", "1", "1")
        assert elem.get_element_unit() == "Amp"

    def test_unit_with_custom_name(self):
        """Test unit detection with custom name parameter."""
        elem = Element("R1", "0", "1", "1k")
        assert elem.get_element_unit("V2") == "Volt"
        assert elem.get_element_unit("C5") == "Farad"


class TestElementDescription:
    """Test element description generation."""

    def test_basic_description(self):
        """Test basic element description."""
        elem = Element("R1", "ground", "node 1", "1k")
        desc = elem.to_description()
        assert "resistor" in desc
        assert "R1" in desc
        assert "1k Ohm" in desc
        assert "ground" in desc
        assert "node 1" in desc

    def test_voltage_source_direction(self):
        """Test voltage source direction text."""
        elem = Element("V1", "0", "N001", "10")
        desc = elem.to_description()
        assert "positive terminal" in desc
        assert "negative terminal" in desc
        assert "ground" in desc
        assert "node 1" in desc

    def test_current_source_direction(self):
        """Test current source direction text."""
        elem = Element("I1", "N001", "0", "1")
        desc = elem.to_description()
        assert "current from the current source is flowing" in desc
        assert "node 1" in desc
        assert "ground" in desc

    def test_waveform_value(self):
        """Test waveform value text."""
        elem = Element("V1", "0", "N001", "PULSE 0 5 1n")
        desc = elem.to_description()
        assert "pulse waveform" in desc

    def test_parallel_connection(self):
        """Test parallel connection description."""
        elem1 = Element("R1", "0", "N001", "1k")
        elem1.set_parallel_connection("R2", "2k Ohm")
        desc = elem1.to_description()
        assert "connected in parallel" in desc
        assert "R2" in desc
        assert "2k Ohm" in desc

    def test_series_connection(self):
        """Test series connection description."""
        elem1 = Element("R1", "0", "N001", "1k")
        elem1.set_series_connection("R2", "node 1", "2k Ohm")
        desc = elem1.to_description()
        assert "connected in series" in desc
        assert "R2" in desc
        assert "2k Ohm" in desc
        assert "connected at node 1" in desc


class TestElementSpecialCases:
    """Test special element cases."""

    def test_no_value(self):
        """Test element with no value."""
        elem = Element("V1", "0", "N001")
        desc = elem.to_description()
        assert "voltage source" in desc
        # Should not contain any unit or value text
        assert "Volt" not in desc

    def test_unknown_element_type(self):
        """Test unknown element type."""
        elem = Element("X1", "0", "N001", "some_value")
        assert elem.get_element_type() == "element"
        assert elem.get_element_unit() == ""

    def test_repr(self):
        """Test element string representation."""
        elem = Element("R1", "0", "N001", "1k")
        repr_str = repr(elem)
        assert "R1" in repr_str
        assert "ground" in repr_str
        assert "node 1" in repr_str
        assert "1k" in repr_str
