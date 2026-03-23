"""Tests for the circuit module."""

import pytest
import tempfile
import os
from netlist_to_text.circuit import Circuit
from netlist_to_text.element import Element


class TestCircuitBasics:
    """Test basic circuit functionality."""

    def test_empty_circuit(self):
        """Test creating an empty circuit."""
        cct = Circuit()
        assert len(cct.elements) == 0
        assert len(cct.nodes) == 0

    def test_add_element(self):
        """Test adding an element to circuit."""
        cct = Circuit()
        elem = Element("R1", "0", "N001", "1k")
        cct.add_element(elem)
        
        assert len(cct.elements) == 1
        assert "ground" in cct.nodes
        assert "node 1" in cct.nodes

    def test_multiple_elements(self):
        """Test adding multiple elements."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "N001", "1k"))
        cct.add_element(Element("R2", "N001", "N002", "2k"))
        cct.add_element(Element("R3", "N002", "0", "3k"))
        
        assert len(cct.elements) == 3
        assert len(cct.nodes) == 3  # ground, node 1, node 2

    def test_count_elements_by_type(self):
        """Test counting elements by type."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("R2", "1", "2", "2k"))
        cct.add_element(Element("C1", "2", "0", "1u"))
        cct.add_element(Element("V1", "0", "1", "10"))
        
        counts = cct.count_elements_by_type()
        assert counts.get("resistor", 0) == 2
        assert counts.get("capacitor", 0) == 1
        assert counts.get("voltage source", 0) == 1


class TestCircuitAnalysis:
    """Test circuit analysis methods."""

    def test_rotatable_elements(self):
        """Test detection of rotatable elements."""
        cct = Circuit()
        
        assert cct.is_rotatable(Element("R1", "0", "1", "1k")) is True
        assert cct.is_rotatable(Element("L1", "0", "1", "1m")) is True
        assert cct.is_rotatable(Element("C1", "0", "1", "1u")) is True
        assert cct.is_rotatable(Element("V1", "0", "1", "10")) is False
        assert cct.is_rotatable(Element("I1", "0", "1", "1")) is False

    def test_parallel_detection(self):
        """Test parallel connection detection."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("R2", "0", "1", "2k"))
        
        cct.find_parallel_connections()
        
        # First element should be marked as parallel
        assert cct.elements[0].parallel_connection_present is True
        assert "parallel" in cct.elements[0].parallel_connection_text
        assert "R2" in cct.elements[0].parallel_connection_text

    def test_parallel_with_swapped_nodes(self):
        """Test parallel detection with swapped nodes (rotatable)."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("L1", "1", "0", "1m"))
        
        cct.find_parallel_connections()
        
        # Should detect parallel connection even with swapped nodes
        assert cct.elements[0].parallel_connection_present is True

    def test_series_detection(self):
        """Test series connection detection."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("R2", "1", "2", "2k"))
        
        cct.find_series_connections()
        
        # Should detect series at node 1
        assert cct.elements[0].series_connection_present is True
        assert "series" in cct.elements[0].series_connection_text
        assert "connected at node 1" in cct.elements[0].series_connection_text

    def test_series_with_parallel_elements(self):
        """Test that parallel elements are not also marked as series."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("R2", "0", "1", "2k"))  # Parallel to R1
        cct.add_element(Element("R3", "1", "2", "3k"))
        
        cct.find_parallel_connections()
        cct.find_series_connections()
        
        # R1 and R2 should be parallel
        assert cct.elements[0].parallel_connection_present is True
        assert cct.elements[1].parallel_connection_present is True
        
        # R3 should be series with the parallel combination
        # But it should connect to node 1 which has 3 connections now
        # So series should not be detected (node has 3 connections)
        assert cct.elements[2].series_connection_present is False

    def test_sort_elements_by_nodes(self):
        """Test sorting elements by node values."""
        cct = Circuit()
        cct.add_element(Element("R2", "0", "N005", "2k"))  # node 5
        cct.add_element(Element("R1", "0", "N001", "1k"))  # node 1
        cct.add_element(Element("R3", "0", "N010", "3k"))  # node 10
        
        cct.sort_elements_by_nodes()
        
        # Should be sorted by node number
        assert cct.elements[0].name == "R1"  # node 1
        assert cct.elements[1].name == "R2"  # node 5
        assert cct.elements[2].name == "R3"  # node 10


class TestCircuitDescription:
    """Test circuit description generation."""

    def test_simple_description(self):
        """Test description for simple circuit."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "N001", "1k"))
        cct.add_element(Element("R2", "N001", "N002", "2k"))
        
        desc = cct.generate_description()
        
        assert "2 elements" in desc
        assert "2 nodes" in desc
        assert "R1" in desc
        assert "R2" in desc
        assert "resistor" in desc

    def test_voltage_divider_description(self):
        """Test description for voltage divider."""
        cct = Circuit()
        cct.add_element(Element("V1", "0", "1", "10"))
        cct.add_element(Element("R1", "1", "2", "1k"))
        cct.add_element(Element("R2", "2", "0", "2k"))
        
        desc = cct.generate_description()
        
        assert "3 elements" in desc
        assert "voltage source" in desc
        assert "V1" in desc
        assert "10 Volt" in desc
        assert "R1" in desc
        assert "R2" in desc

    def test_parallel_description(self):
        """Test description with parallel elements."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("R2", "0", "1", "2k"))
        
        desc = cct.generate_description()
        
        assert "parallel" in desc
        assert "R1" in desc
        assert "R2" in desc

    def test_series_description(self):
        """Test description with series elements."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("R2", "1", "2", "2k"))
        
        desc = cct.generate_description()
        
        assert "series" in desc
        assert "R1" in desc
        assert "R2" in desc
        assert "connected at" in desc


class TestCircuitFromFile:
    """Test loading circuit from file."""

    def test_load_from_spice_file(self):
        """Test loading circuit from SPICE file."""
        content = """* Simple circuit
V1 0 1 10
R1 1 2 1k
R2 2 0 2k
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.net', delete=False) as f:
            f.write(content)
            f.flush()
            
            cct = Circuit()
            cct.from_netlist_file(f.name)
            
            assert len(cct.elements) == 3
            assert cct.elements[0].name == "V1"
            assert cct.elements[1].name == "R1"
            assert cct.elements[2].name == "R2"
            
            os.unlink(f.name)

    def test_description_from_file(self):
        """Test generating description from file."""
        content = """* Voltage divider
V1 0 N001 10
R1 N001 N002 1k
R2 N002 0 2k
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.net', delete=False) as f:
            f.write(content)
            f.flush()
            
            cct = Circuit()
            cct.from_netlist_file(f.name)
            desc = cct.generate_description()
            
            assert "3 elements" in desc
            assert "voltage source" in desc
            assert "10 Volt" in desc
            
            os.unlink(f.name)


class TestCircuitRepresentation:
    """Test circuit string representation."""

    def test_repr(self):
        """Test circuit string representation."""
        cct = Circuit()
        cct.add_element(Element("R1", "0", "1", "1k"))
        cct.add_element(Element("R2", "1", "2", "2k"))
        
        repr_str = repr(cct)
        assert "elements=2" in repr_str
        assert "nodes=2" in repr_str
